from __future__ import annotations

from typing import Any


def first_relation(row: dict[str, Any], key: str) -> dict[str, Any]:
    value = row.get(key) or {}
    if isinstance(value, list):
        return value[0] if value else {}
    return value


def normalize_initial(row: dict[str, Any] | None) -> dict[str, Any]:
    row = row or {}
    return {
        "eligibility": row.get("eligibility") or row.get("proposed_eligibility") or "KEEP",
        "remove_reason": row.get("remove_reason") or "",
        "C_label": row.get("C_label") or row.get("c_label") or row.get("proposed_c") or "C0",
        "S_label": row.get("S_label") or row.get("s_label") or row.get("proposed_s") or "S0",
        "A_label": row.get("A_label") or row.get("a_label") or row.get("proposed_a") or "A0",
        "uncertain": row.get("uncertain") in {True, "YES", "yes", "true", "TRUE"},
        "uncertainty_reason": row.get("uncertainty_reason") or "",
        "evidence": row.get("evidence") or "",
        "rule_id": row.get("rule_id") or "",
        "note": row.get("note") or "",
        "guideline_version": row.get("guideline_version") or "p1.0-mock",
    }


def normalize_prediction(row: dict[str, Any] | None) -> dict[str, Any]:
    row = row or {}
    return normalize_initial({
        "eligibility": row.get("predicted_eligibility"),
        "c_label": row.get("predicted_c"),
        "s_label": row.get("predicted_s"),
        "a_label": row.get("predicted_a"),
        "uncertain": row.get("uncertain"),
        "uncertainty_reason": row.get("uncertainty_reason"),
        "evidence": row.get("evidence"),
        "guideline_version": row.get("guideline_version"),
    })


def to_supabase_annotation(labels: dict[str, Any], *, record_id: str, annotator_code: str) -> dict[str, Any]:
    eligibility = labels.get("eligibility")
    return {
        "record_id": record_id,
        "annotator_code": annotator_code,
        "eligibility": eligibility,
        "remove_reason": labels.get("remove_reason") if eligibility == "REMOVE" else None,
        "c_label": None if eligibility == "REMOVE" else labels.get("C_label"),
        "s_label": None if eligibility == "REMOVE" else labels.get("S_label"),
        "a_label": None if eligibility == "REMOVE" else labels.get("A_label"),
        "uncertain": "YES" if labels.get("uncertain") else "NO",
        "uncertainty_reason": labels.get("uncertainty_reason") or None,
        "evidence": labels.get("evidence") or None,
        "rule_id": labels.get("rule_id") or None,
        "note": labels.get("note") or None,
        "guideline_version": labels.get("guideline_version") or "p1.0-mock",
    }
