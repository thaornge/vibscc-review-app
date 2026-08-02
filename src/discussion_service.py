from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .repository_base import Repository
from .review_service import AccessError, ConflictError
from .validators import validate_annotation


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DiscussionService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def list_for_reviewer(self, reviewer_id: str) -> list[dict[str, Any]]:
        data = self.repository.snapshot()
        result = []
        for case in data["cases"].values():
            if case["case_status"] not in {"DISCUSSION_REQUIRED", "DISCUSSION_IN_PROGRESS"}:
                continue
            participants = [a for a in data["assignments"].values() if a["case_id"] == case["case_id"]]
            if reviewer_id not in {a["reviewer_id"] for a in participants}:
                continue
            labels = [{**data["annotations"][a["assignment_id"]], "review_slot": a["review_slot"], "annotator_code": a["reviewer_id"]} for a in sorted(participants, key=lambda value: value["review_slot"])]
            result.append({"case": case, "record": data["records"][case["record_id"]], "labels": labels, "discussion": data["discussions"].get(case["case_id"])})
        return result

    def propose(self, reviewer_id: str, case_id: str, proposal: Mapping[str, Any], rationale: str) -> None:
        validate_annotation({**proposal, "decision_action": "BLIND_LABEL"})
        if not rationale.strip():
            raise ValueError("Discussion rationale is required")

        def operation(data: dict[str, Any]) -> None:
            case = data["cases"].get(case_id)
            if not case or case["case_status"] not in {"DISCUSSION_REQUIRED", "DISCUSSION_IN_PROGRESS"}:
                raise ConflictError("Case is not open for discussion")
            participants = {a["reviewer_id"] for a in data["assignments"].values() if a["case_id"] == case_id}
            if reviewer_id not in participants:
                raise AccessError("Only assigned reviewers may propose")
            now = _now()
            data["discussions"][case_id] = {"case_id": case_id, "discussion_status": "PENDING_CONFIRMATION", "proposal": dict(proposal), "proposed_by": reviewer_id, "confirmed_by_slot_1": "", "confirmed_by_slot_2": "", "rationale": rationale.strip(), "resolved_at": ""}
            case["case_status"] = "DISCUSSION_IN_PROGRESS"
            data["audit_events"].append({"event_type": "DISCUSSION_PROPOSE", "actor_id": reviewer_id, "case_id": case_id, "created_at": now})
        self.repository.atomic_update(operation)

    def respond(self, reviewer_id: str, case_id: str, confirm: bool, rationale: str = "") -> str:
        def operation(data: dict[str, Any]) -> str:
            case = data["cases"].get(case_id)
            discussion = data["discussions"].get(case_id)
            if not case or not discussion or discussion["discussion_status"] != "PENDING_CONFIRMATION":
                raise ConflictError("No proposal is waiting for confirmation")
            participants = [a for a in data["assignments"].values() if a["case_id"] == case_id]
            if reviewer_id not in {a["reviewer_id"] for a in participants} or reviewer_id == discussion["proposed_by"]:
                raise AccessError("The other assigned reviewer must respond")
            now = _now()
            if confirm:
                by_slot = {a["review_slot"]: a["reviewer_id"] for a in participants}
                discussion["confirmed_by_slot_1"] = by_slot.get(1, "")
                discussion["confirmed_by_slot_2"] = by_slot.get(2, "")
                discussion["discussion_status"] = "RESOLVED"
                discussion["resolved_at"] = now
                case["case_status"] = "RESOLVED_DISCUSSION"
                case["resolved_at"] = now
            else:
                if not rationale.strip():
                    raise ValueError("Reject/escalate requires rationale")
                discussion["discussion_status"] = "ESCALATED"
                discussion["rationale"] += f" | Reject: {rationale.strip()}"
                case["case_status"] = "ADJUDICATION_REQUIRED"
            data["audit_events"].append({"event_type": "DISCUSSION_CONFIRM" if confirm else "DISCUSSION_REJECT", "actor_id": reviewer_id, "case_id": case_id, "created_at": now})
            return case["case_status"]
        return self.repository.atomic_update(operation)

