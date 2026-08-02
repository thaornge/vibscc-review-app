from __future__ import annotations

from typing import Any, Mapping

from .constants import A_LABELS, C_LABELS, ELIGIBILITY, REMOVE_REASON_OPTIONS, S_LABELS


class ValidationError(ValueError):
    pass


def normalized_tuple(annotation: Mapping[str, Any]) -> tuple[str, str, str, str]:
    return tuple(str(annotation.get(key) or "") for key in ("eligibility", "C_label", "S_label", "A_label"))  # type: ignore[return-value]


def validate_annotation(annotation: Mapping[str, Any], *, require_action: bool = True) -> None:
    errors: list[str] = []
    eligibility = str(annotation.get("eligibility") or "")
    c_label = str(annotation.get("C_label") or "")
    s_label = str(annotation.get("S_label") or "")
    a_label = str(annotation.get("A_label") or "")

    if require_action and annotation.get("decision_action") not in {"BLIND_LABEL", "ACCEPT", "EDIT"}:
        errors.append("decision_action must be BLIND_LABEL, ACCEPT, or EDIT")
    if eligibility not in ELIGIBILITY:
        errors.append("eligibility must be KEEP or REMOVE")
    elif eligibility == "REMOVE":
        if any((c_label, s_label, a_label)):
            errors.append("REMOVE requires blank C/S/A")
        remove_reason = str(annotation.get("remove_reason") or "").strip()
        if not remove_reason:
            errors.append("REMOVE requires remove_reason")
        elif remove_reason not in REMOVE_REASON_OPTIONS:
            errors.append("REMOVE requires a valid remove_reason")
        elif remove_reason == "OTHER_REMOVE" and not str(annotation.get("note") or "").strip():
            errors.append("OTHER_REMOVE requires note")
    else:
        if c_label not in C_LABELS or s_label not in S_LABELS or a_label not in A_LABELS:
            errors.append("KEEP requires valid C/S/A labels")
        elif c_label == "C0" and (s_label != "S0" or a_label != "A0"):
            errors.append("C0 requires S0 and A0")
        elif c_label == "C1" and (s_label == "S0" or a_label == "A0"):
            errors.append("C1 requires S1-S6 and A1-A7")
        elif c_label == "C2" and (s_label != "S0" or a_label == "A0"):
            errors.append("C2 requires S0 and A1-A7")

    uncertain = bool(annotation.get("uncertain", False))
    if uncertain and not str(annotation.get("uncertainty_reason") or "").strip():
        errors.append("uncertain=true requires uncertainty_reason")
    if annotation.get("decision_action") == "EDIT" and not str(annotation.get("note") or "").strip():
        errors.append("EDIT requires a short note")
    if not str(annotation.get("guideline_version") or "").strip():
        errors.append("guideline_version is required")

    if errors:
        raise ValidationError("; ".join(errors))
