import pytest

from src.validators import ValidationError, validate_annotation


def valid(**changes):
    value = {"decision_action": "BLIND_LABEL", "eligibility": "KEEP", "remove_reason": "", "C_label": "C1", "S_label": "S2", "A_label": "A3", "uncertain": False, "uncertainty_reason": "", "evidence": "e", "rule_id": "R1", "note": "", "guideline_version": "p1.0-mock"}
    value.update(changes)
    return value


@pytest.mark.parametrize("annotation", [
    valid(C_label="C0", S_label="S0", A_label="A0"),
    valid(C_label="C2", S_label="S0", A_label="A7"),
    valid(eligibility="REMOVE", remove_reason="EMPTY_OR_WHITESPACE", C_label="", S_label="", A_label=""),
    valid(eligibility="REMOVE", remove_reason="OTHER_REMOVE", C_label="", S_label="", A_label="", note="Specific reason"),
])
def test_valid_constraints(annotation):
    validate_annotation(annotation)


@pytest.mark.parametrize("annotation", [
    valid(C_label="C0", S_label="S1", A_label="A0"),
    valid(C_label="C1", S_label="S0", A_label="A2"),
    valid(C_label="C2", S_label="S0", A_label="A0"),
    valid(eligibility="REMOVE", remove_reason="", C_label="", S_label="", A_label=""),
    valid(eligibility="REMOVE", remove_reason="OUT_OF_SCOPE", C_label="", S_label="", A_label=""),
    valid(eligibility="REMOVE", remove_reason="OTHER_REMOVE", C_label="", S_label="", A_label="", note=""),
    valid(eligibility="REMOVE", remove_reason="EMPTY_OR_WHITESPACE", C_label="C0", S_label="S0", A_label="A0"),
    valid(uncertain=True, uncertainty_reason=""),
])
def test_invalid_constraints(annotation):
    with pytest.raises(ValidationError):
        validate_annotation(annotation)
