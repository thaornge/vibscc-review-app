from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_mock_store() -> dict[str, Any]:
    users = {
        "ANN_01": {"annotator_code": "ANN_01", "display_name": "Reviewer 1", "role": "REVIEWER", "is_active": True},
        "ANN_02": {"annotator_code": "ANN_02", "display_name": "Reviewer 2", "role": "REVIEWER", "is_active": True},
        "ANN_03": {"annotator_code": "ANN_03", "display_name": "Reviewer 3", "role": "REVIEWER", "is_active": True},
        "ANN_04": {"annotator_code": "ANN_04", "display_name": "Reviewer 4", "role": "REVIEWER", "is_active": True},
        "ADMIN_PHUC": {"annotator_code": "ADMIN_PHUC", "display_name": "Phúc (Admin)", "role": "ADMIN", "is_active": True},
    }
    specs = [
        ("V001", "Bạn ấy rất tử tế và luôn giúp đỡ mọi người.", "SINGLE_VISIBLE_REVIEW", "CONSENSUS", False, 1, "PRODUCTION"),
        ("V002", "Nhóm đó lúc nào cũng làm việc thiếu chuyên nghiệp.", "SINGLE_VISIBLE_REVIEW", "CONSENSUS", False, 1, "PRODUCTION"),
        ("B001", "Tôi không tin tưởng người thuộc nhóm này.", "DOUBLE_BLIND", "DISAGREEMENT_C", False, 2, "PRODUCTION"),
        ("B002", "Câu này có hàm ý mơ hồ và cần người kiểm tra.", "DOUBLE_BLIND", "LLM_UNCERTAIN", False, 2, "PRODUCTION"),
        ("A001", "Một nhận xét đồng thuận được chọn kiểm tra ngẫu nhiên.", "DOUBLE_BLIND_AUDIT", "AUDIT", True, 2, "PRODUCTION"),
        ("I001", "Đầu ra mô hình lỗi schema nên phải review blind.", "DOUBLE_BLIND", "INVALID_PREDICTION", False, 2, "PRODUCTION"),
        ("T001", "Mẫu test reserve chỉ có văn bản và không có dự đoán LLM.", "DOUBLE_BLIND_TEST", "TEST_RESERVE", False, 2, "TEST_RESERVE_CANDIDATE"),
        ("T002", "Mẫu test reserve phục vụ luồng thảo luận và phân xử.", "DOUBLE_BLIND_TEST", "TEST_RESERVE", False, 2, "TEST_RESERVE_CANDIDATE"),
    ]
    records: dict[str, Any] = {}
    cases: dict[str, Any] = {}
    predictions: dict[str, list[dict[str, Any]]] = {}
    assignments: dict[str, Any] = {}
    reviewers = [("ANN_01", "ANN_02"), ("ANN_03", "ANN_04")]
    for index, (record_id, text, route, reason, audit, required, role) in enumerate(specs):
        case_id = f"CASE_{record_id}"
        records[record_id] = {
            "record_id": record_id,
            "text_annotation": text,
            "guideline_version": "p1.0-mock",
            "batch_id": "MOCK_CP2_20260802",
            "data_role": role,
            "import_run_id": "IMPORT_MOCK_CP2",
        }
        cases[case_id] = {
            "case_id": case_id,
            "record_id": record_id,
            "review_route": route,
            "route_reason": reason,
            "audit_flag": audit,
            "required_reviews": required,
            "case_status": "ASSIGNED",
            "import_run_id": "IMPORT_MOCK_CP2",
            "resolved_at": "",
        }
        if route != "DOUBLE_BLIND_TEST":
            consensus = {"eligibility": "KEEP", "C_label": "C0", "S_label": "S0", "A_label": "A0"}
            second = dict(consensus)
            if reason == "DISAGREEMENT_C":
                second = {"eligibility": "KEEP", "C_label": "C1", "S_label": "S2", "A_label": "A3"}
            predictions[record_id] = [
                {"model_slot": 1, "model_id": "mock-model-1", **consensus, "uncertain": reason == "LLM_UNCERTAIN", "evidence": "mock evidence", "parse_status": "VALID", "constraint_valid": True},
                {"model_slot": 2, "model_id": "mock-model-2", **second, "uncertain": False, "evidence": "mock evidence", "parse_status": "INVALID_JSON" if reason == "INVALID_PREDICTION" else "VALID", "constraint_valid": reason != "INVALID_PREDICTION"},
            ]
        pair = reviewers[index % 2]
        for slot in range(1, required + 1):
            reviewer = pair[slot - 1]
            assignment_id = f"ASG_{record_id}_{slot}"
            assignments[assignment_id] = {
                "assignment_id": assignment_id,
                "case_id": case_id,
                "reviewer_id": reviewer,
                "review_slot": slot,
                "visibility_mode": "VISIBLE" if route == "SINGLE_VISIBLE_REVIEW" else "BLIND",
                "assignment_status": "ASSIGNED",
                "row_version": 0,
                "assigned_at": _now(),
                "started_at": "",
                "submitted_at": "",
            }
    annotations = {
        "ASG_B001_1": {"decision_action": "BLIND_LABEL", "eligibility": "KEEP", "remove_reason": "", "C_label": "C0", "S_label": "S0", "A_label": "A0", "uncertain": False, "uncertainty_reason": "", "evidence": "Cách nói khái quát hóa nhóm.", "rule_id": "MOCK-R1", "note": "", "guideline_version": "p1.0-mock", "save_status": "SUBMITTED", "row_version": 1, "started_at": _now(), "submitted_at": _now()},
        "ASG_B001_2": {"decision_action": "BLIND_LABEL", "eligibility": "KEEP", "remove_reason": "", "C_label": "C1", "S_label": "S2", "A_label": "A3", "uncertain": False, "uncertainty_reason": "", "evidence": "Cách nói nhắm tới nhóm được đề cập.", "rule_id": "MOCK-R2", "note": "", "guideline_version": "p1.0-mock", "save_status": "SUBMITTED", "row_version": 1, "started_at": _now(), "submitted_at": _now()},
        "ASG_T002_1": {"decision_action": "BLIND_LABEL", "eligibility": "KEEP", "remove_reason": "", "C_label": "C1", "S_label": "S3", "A_label": "A2", "uncertain": False, "uncertainty_reason": "", "evidence": "Mock evidence slot 1.", "rule_id": "MOCK-R3", "note": "", "guideline_version": "p1.0-mock", "save_status": "SUBMITTED", "row_version": 1, "started_at": _now(), "submitted_at": _now()},
        "ASG_T002_2": {"decision_action": "BLIND_LABEL", "eligibility": "KEEP", "remove_reason": "", "C_label": "C2", "S_label": "S0", "A_label": "A5", "uncertain": False, "uncertainty_reason": "", "evidence": "Mock evidence slot 2.", "rule_id": "MOCK-R4", "note": "", "guideline_version": "p1.0-mock", "save_status": "SUBMITTED", "row_version": 1, "started_at": _now(), "submitted_at": _now()},
    }
    for assignment_id in annotations:
        assignments[assignment_id]["assignment_status"] = "SUBMITTED"
        assignments[assignment_id]["row_version"] = 1
        assignments[assignment_id]["started_at"] = annotations[assignment_id]["started_at"]
        assignments[assignment_id]["submitted_at"] = annotations[assignment_id]["submitted_at"]
    cases["CASE_B001"]["case_status"] = "DISCUSSION_REQUIRED"
    cases["CASE_T002"]["case_status"] = "ADJUDICATION_REQUIRED"
    discussions = {
        "CASE_T002": {"case_id": "CASE_T002", "discussion_status": "ESCALATED", "proposal": {"eligibility": "KEEP", "remove_reason": "", "C_label": "C1", "S_label": "S3", "A_label": "A2", "uncertain": False, "uncertainty_reason": "", "evidence": "Proposal evidence", "rule_id": "MOCK-R3", "note": "", "guideline_version": "p1.0-mock"}, "proposed_by": "ANN_01", "confirmed_by_slot_1": "", "confirmed_by_slot_2": "", "rationale": "Hai reviewer chưa thống nhất; chuyển admin phân xử.", "resolved_at": ""}
    }
    return {
        "schema_version": "verify-app-mock-v1",
        "users": users,
        "records": records,
        "predictions": predictions,
        "cases": cases,
        "assignments": assignments,
        "annotations": annotations,
        "discussions": discussions,
        "adjudications": {},
        "audit_events": [],
    }
