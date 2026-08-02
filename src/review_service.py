from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .constants import DOUBLE_ROUTES, VISIBLE_ROUTE
from .repository_base import Repository
from .validators import normalized_tuple, validate_annotation


class ConflictError(RuntimeError):
    pass


class AccessError(PermissionError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ReviewService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def list_assignments(self, reviewer_id: str) -> list[dict[str, Any]]:
        data = self.repository.snapshot()
        result = []
        for assignment in data["assignments"].values():
            if assignment["reviewer_id"] != reviewer_id:
                continue
            case = data["cases"][assignment["case_id"]]
            record = data["records"][case["record_id"]]
            result.append({**assignment, "record_id": record["record_id"], "case_status": case["case_status"], "text_annotation": record["text_annotation"]})
        return sorted(result, key=lambda row: row["assignment_id"])

    def reviewer_view(self, reviewer_id: str, assignment_id: str) -> dict[str, Any]:
        data = self.repository.snapshot()
        assignment = data["assignments"].get(assignment_id)
        if not assignment or assignment["reviewer_id"] != reviewer_id:
            raise AccessError("Assignment does not belong to this reviewer")
        case = data["cases"][assignment["case_id"]]
        record = data["records"][case["record_id"]]
        view = {
            "assignment": assignment,
            "record": {key: record[key] for key in ("record_id", "text_annotation", "guideline_version", "batch_id", "data_role")},
            "case_status": case["case_status"],
            "visibility_mode": assignment["visibility_mode"],
            "draft": data["annotations"].get(assignment_id),
        }
        if assignment["visibility_mode"] == "VISIBLE":
            predictions = data["predictions"].get(record["record_id"], [])
            if len(predictions) != 2 or normalized_tuple(predictions[0]) != normalized_tuple(predictions[1]):
                raise ConflictError("Visible case lacks exact valid two-model consensus")
            view["llm_consensus"] = predictions[0]
        return view

    def save_draft(self, reviewer_id: str, assignment_id: str, annotation: Mapping[str, Any], expected_version: int) -> int:
        def operation(data: dict[str, Any]) -> int:
            assignment = data["assignments"].get(assignment_id)
            if not assignment or assignment["reviewer_id"] != reviewer_id:
                raise AccessError("Assignment does not belong to this reviewer")
            if assignment["assignment_status"] == "SUBMITTED":
                raise ConflictError("Submitted initial annotation is locked")
            if assignment["row_version"] != expected_version:
                raise ConflictError("Draft version changed; reload before saving")
            now = _now()
            assignment["assignment_status"] = "IN_PROGRESS"
            assignment["started_at"] = assignment["started_at"] or now
            assignment["row_version"] += 1
            data["annotations"][assignment_id] = {**dict(annotation), "save_status": "DRAFT", "row_version": assignment["row_version"], "updated_at": now}
            data["cases"][assignment["case_id"]]["case_status"] = "IN_REVIEW"
            data["audit_events"].append({"event_type": "SAVE_DRAFT", "actor_id": reviewer_id, "assignment_id": assignment_id, "created_at": now})
            return assignment["row_version"]
        return self.repository.atomic_update(operation)

    def submit(self, reviewer_id: str, assignment_id: str, annotation: Mapping[str, Any], expected_version: int) -> str:
        validate_annotation(annotation)

        def operation(data: dict[str, Any]) -> str:
            assignment = data["assignments"].get(assignment_id)
            if not assignment or assignment["reviewer_id"] != reviewer_id:
                raise AccessError("Assignment does not belong to this reviewer")
            if assignment["assignment_status"] == "SUBMITTED":
                raise ConflictError("Initial annotation is already submitted and locked")
            if assignment["row_version"] != expected_version:
                raise ConflictError("Submission version changed; reload before submitting")
            case = data["cases"][assignment["case_id"]]
            route = case["review_route"]
            action = annotation["decision_action"]
            if route in DOUBLE_ROUTES and action != "BLIND_LABEL":
                raise ConflictError("Blind routes require BLIND_LABEL")
            if route == VISIBLE_ROUTE and action not in {"ACCEPT", "EDIT"}:
                raise ConflictError("Visible route requires ACCEPT or EDIT")
            if action == "ACCEPT":
                predictions = data["predictions"].get(case["record_id"], [])
                if len(predictions) != 2 or normalized_tuple(annotation) != normalized_tuple(predictions[0]) or normalized_tuple(predictions[0]) != normalized_tuple(predictions[1]):
                    raise ConflictError("ACCEPT must preserve the exact two-model consensus tuple")
            now = _now()
            assignment["assignment_status"] = "SUBMITTED"
            assignment["started_at"] = assignment["started_at"] or now
            assignment["submitted_at"] = now
            assignment["row_version"] += 1
            data["annotations"][assignment_id] = {**dict(annotation), "save_status": "SUBMITTED", "row_version": assignment["row_version"], "started_at": assignment["started_at"], "submitted_at": now}
            case_assignments = [a for a in data["assignments"].values() if a["case_id"] == case["case_id"]]
            submitted = [a for a in case_assignments if a["assignment_status"] == "SUBMITTED"]
            if route == VISIBLE_ROUTE:
                case["case_status"] = "RESOLVED_VISIBLE_ACCEPT" if action == "ACCEPT" else "RESOLVED_VISIBLE_EDIT"
                case["resolved_at"] = now
            elif len(submitted) < case["required_reviews"]:
                case["case_status"] = "WAITING_SECOND_REVIEW"
            else:
                labels = [data["annotations"][a["assignment_id"]] for a in sorted(submitted, key=lambda value: value["review_slot"])]
                if normalized_tuple(labels[0]) == normalized_tuple(labels[1]):
                    case["case_status"] = "RESOLVED_HUMAN_AGREEMENT"
                    case["resolved_at"] = now
                else:
                    case["case_status"] = "DISCUSSION_REQUIRED"
            data["audit_events"].append({"event_type": "SUBMIT", "actor_id": reviewer_id, "assignment_id": assignment_id, "case_id": case["case_id"], "created_at": now})
            return case["case_status"]
        return self.repository.atomic_update(operation)

