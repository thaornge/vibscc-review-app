import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.constants import CaseStatus, DOUBLE_ROUTES, Route
from src.repository_base import ReviewRepository
from src.state_machine import assert_transition
from src.validators import label_tuple, normalized_annotation


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RepositoryError(ValueError):
    pass


class FakeRepository(ReviewRepository):
    """JSON-backed mock repository. It persists across app reloads, not for production."""

    def __init__(self, state_path: str | Path | None = None, seed_path: str | Path | None = None):
        root = Path(__file__).resolve().parents[1]
        self.state_path = Path(state_path or root / "mock_data/runtime_state.json")
        seed_path = Path(seed_path or root / "mock_data/seed_state.json")
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.state_path.exists():
            self.state_path.write_text(seed_path.read_text(encoding="utf-8"), encoding="utf-8")
        self._load()

    def _load(self) -> None:
        self.data = json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.state_path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def reset(self, seed_path: str | Path | None = None) -> None:
        seed = Path(seed_path or Path(__file__).resolve().parents[1] / "mock_data/seed_state.json")
        self.state_path.write_text(seed.read_text(encoding="utf-8"), encoding="utf-8")
        self._load()

    def users(self) -> list[dict[str, Any]]:
        return copy.deepcopy(self.data["users"])

    def _case(self, case_id: str) -> dict[str, Any]:
        try:
            return next(c for c in self.data["cases"] if c["case_id"] == case_id)
        except StopIteration as exc:
            raise RepositoryError("Không tìm thấy case") from exc

    def _assignment(self, case: dict[str, Any], user_id: str) -> dict[str, Any]:
        try:
            return next(a for a in case["assignments"] if a["reviewer_id"] == user_id)
        except StopIteration as exc:
            raise RepositoryError("Người dùng không được assign case này") from exc

    def assignments_for(self, user_id: str) -> list[dict[str, Any]]:
        result = []
        for case in self.data["cases"]:
            for assignment in case["assignments"]:
                if assignment["reviewer_id"] == user_id:
                    result.append({"case_id": case["case_id"], "record_id": case["record_id"], "route": case["route"], "status": case["status"], "assignment_status": assignment["status"]})
        return result

    def case_for_reviewer(self, case_id: str, user_id: str) -> dict[str, Any]:
        case = self._case(case_id)
        assignment = self._assignment(case, user_id)
        view = {k: copy.deepcopy(case[k]) for k in ("case_id", "record_id", "text_annotation", "guideline_version", "batch_id", "route", "status")}
        view["assignment"] = copy.deepcopy(assignment)
        if case["route"] == Route.SINGLE_VISIBLE_REVIEW:
            view["llm_consensus"] = copy.deepcopy(case.get("llm_consensus"))
        if case["status"] in {CaseStatus.DISCUSSION_REQUIRED, CaseStatus.DISCUSSION_IN_PROGRESS, CaseStatus.RESOLVED_DISCUSSION, CaseStatus.ADJUDICATION_REQUIRED, CaseStatus.RESOLVED_ADJUDICATION}:
            if all(a["status"] == "SUBMITTED" for a in case["assignments"]):
                view["submitted_annotations"] = [{"reviewer_id": a["reviewer_id"], **copy.deepcopy(a["annotation"])} for a in case["assignments"]]
                view["discussion"] = copy.deepcopy(case.get("discussion"))
        return view

    def save_draft(self, case_id: str, user_id: str, annotation: dict[str, Any]) -> None:
        case, assignment = self._case(case_id), self._assignment(self._case(case_id), user_id)
        if assignment["status"] == "SUBMITTED":
            raise RepositoryError("Annotation đã submit và bị khóa")
        assignment.update({"status": "IN_PROGRESS", "draft": copy.deepcopy(annotation), "updated_at": now()})
        if case["status"] == CaseStatus.ASSIGNED:
            assert_transition(case["status"], CaseStatus.IN_REVIEW)
            case["status"] = CaseStatus.IN_REVIEW
        self._save()

    def submit(self, case_id: str, user_id: str, annotation: dict[str, Any], action: str) -> None:
        case, assignment = self._case(case_id), self._assignment(self._case(case_id), user_id)
        if assignment["status"] == "SUBMITTED":
            raise RepositoryError("Không thể submit hai lần")
        annotation = normalized_annotation(annotation)
        if case["route"] == Route.SINGLE_VISIBLE_REVIEW and action not in {"ACCEPT", "EDIT"}:
            raise RepositoryError("Visible review chỉ cho phép ACCEPT hoặc EDIT")
        if case["route"] in DOUBLE_ROUTES and action != "BLIND_LABEL":
            raise RepositoryError("Blind review yêu cầu action BLIND_LABEL")
        assignment.update({"status": "SUBMITTED", "draft": None, "annotation": annotation, "decision_action": action, "submitted_at": now()})
        submitted = [a for a in case["assignments"] if a["status"] == "SUBMITTED"]
        if case["route"] == Route.SINGLE_VISIBLE_REVIEW:
            target = CaseStatus.RESOLVED_VISIBLE_ACCEPT if action == "ACCEPT" else CaseStatus.RESOLVED_VISIBLE_EDIT
        elif len(submitted) == 1:
            target = CaseStatus.WAITING_SECOND_REVIEW
        elif label_tuple(submitted[0]["annotation"]) == label_tuple(submitted[1]["annotation"]):
            target = CaseStatus.RESOLVED_HUMAN_AGREEMENT
        else:
            target = CaseStatus.DISCUSSION_REQUIRED
        assert_transition(case["status"], target)
        case["status"] = target
        self._save()

    def discussion_cases_for(self, user_id: str) -> list[dict[str, Any]]:
        allowed = {CaseStatus.DISCUSSION_REQUIRED, CaseStatus.DISCUSSION_IN_PROGRESS}
        return [self.case_for_reviewer(c["case_id"], user_id) for c in self.data["cases"] if c["status"] in allowed and any(a["reviewer_id"] == user_id for a in c["assignments"])]

    def propose(self, case_id: str, user_id: str, labels: dict[str, Any], rationale: str) -> None:
        case = self._case(case_id); self._assignment(case, user_id)
        if case["status"] != CaseStatus.DISCUSSION_REQUIRED:
            raise RepositoryError("Case chưa sẵn sàng discussion")
        labels = normalized_annotation(labels)
        if not rationale.strip(): raise RepositoryError("Proposal bắt buộc có rationale")
        assert_transition(case["status"], CaseStatus.DISCUSSION_IN_PROGRESS)
        case["discussion"] = {"status": "PENDING_CONFIRMATION", "proposed_by": user_id, "labels": labels, "rationale": rationale, "created_at": now()}
        case["status"] = CaseStatus.DISCUSSION_IN_PROGRESS
        self._save()

    def respond(self, case_id: str, user_id: str, confirm: bool, rationale: str) -> None:
        case = self._case(case_id); self._assignment(case, user_id)
        discussion = case.get("discussion")
        if case["status"] != CaseStatus.DISCUSSION_IN_PROGRESS or not discussion:
            raise RepositoryError("Không có proposal đang chờ")
        if discussion["proposed_by"] == user_id: raise RepositoryError("Người đề xuất không thể tự xác nhận")
        if not rationale.strip(): raise RepositoryError("Bắt buộc có rationale")
        target = CaseStatus.RESOLVED_DISCUSSION if confirm else CaseStatus.ADJUDICATION_REQUIRED
        assert_transition(case["status"], target)
        discussion.update({"status": "RESOLVED" if confirm else "ESCALATED", "responded_by": user_id, "response_rationale": rationale, "resolved_at": now()})
        case["status"] = target
        self._save()

    def adjudication_cases(self) -> list[dict[str, Any]]:
        return copy.deepcopy([c for c in self.data["cases"] if c["status"] == CaseStatus.ADJUDICATION_REQUIRED])

    def adjudicate(self, case_id: str, admin_id: str, labels: dict[str, Any], rationale: str) -> None:
        user = next((u for u in self.data["users"] if u["user_id"] == admin_id), None)
        if not user or user["role"] != "ADMIN": raise RepositoryError("Chỉ ADMIN được adjudicate")
        case = self._case(case_id)
        if case["status"] != CaseStatus.ADJUDICATION_REQUIRED: raise RepositoryError("Case chưa cần adjudication")
        if not rationale.strip(): raise RepositoryError("Adjudication bắt buộc có rationale")
        labels = normalized_annotation(labels)
        assert_transition(case["status"], CaseStatus.RESOLVED_ADJUDICATION)
        case["adjudication"] = {"adjudicator_id": admin_id, "labels": labels, "rationale": rationale, "resolved_at": now()}
        case["status"] = CaseStatus.RESOLVED_ADJUDICATION
        self._save()
