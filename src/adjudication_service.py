from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from .repository_base import Repository
from .review_service import AccessError, ConflictError
from .validators import validate_annotation


class AdjudicationService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def list_pending(self, admin_id: str) -> list[dict[str, Any]]:
        data = self.repository.snapshot()
        user = data["users"].get(admin_id)
        if not user or user["role"] != "ADMIN":
            raise AccessError("Admin role required")
        return [{"case": case, "record": data["records"][case["record_id"]], "discussion": data["discussions"].get(case["case_id"])} for case in data["cases"].values() if case["case_status"] == "ADJUDICATION_REQUIRED"]

    def resolve(self, admin_id: str, case_id: str, annotation: Mapping[str, Any], rationale: str) -> None:
        validate_annotation({**annotation, "decision_action": "BLIND_LABEL"})
        if not rationale.strip():
            raise ValueError("Adjudication rationale is required")

        def operation(data: dict[str, Any]) -> None:
            user = data["users"].get(admin_id)
            case = data["cases"].get(case_id)
            if not user or user["role"] != "ADMIN":
                raise AccessError("Admin role required")
            if not case or case["case_status"] != "ADJUDICATION_REQUIRED":
                raise ConflictError("Case is not awaiting adjudication")
            now = datetime.now(timezone.utc).isoformat()
            data["adjudications"][case_id] = {"case_id": case_id, **dict(annotation), "adjudicator_code": admin_id, "rationale": rationale.strip(), "resolved_at": now}
            case["case_status"] = "RESOLVED_ADJUDICATION"
            case["resolved_at"] = now
            data["audit_events"].append({"event_type": "ADJUDICATE", "actor_id": admin_id, "case_id": case_id, "created_at": now})
        self.repository.atomic_update(operation)

