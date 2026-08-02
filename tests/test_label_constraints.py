import pytest
from src.validators import ValidationError, validate_annotation


@pytest.mark.parametrize("labels", [
    {"eligibility": "KEEP", "C_label": "C0", "S_label": "S0", "A_label": "A0"},
    {"eligibility": "KEEP", "C_label": "C1", "S_label": "S6", "A_label": "A7"},
    {"eligibility": "KEEP", "C_label": "C2", "S_label": "S0", "A_label": "A1"},
    {"eligibility": "REMOVE", "C_label": None, "S_label": None, "A_label": None, "remove_reason": "OUT_OF_SCOPE"},
])
def test_valid_constraints(labels):
    validate_annotation(labels)


@pytest.mark.parametrize("labels", [
    {"eligibility": "KEEP", "C_label": "C0", "S_label": "S2", "A_label": "A0"},
    {"eligibility": "KEEP", "C_label": "C1", "S_label": "S0", "A_label": "A2"},
    {"eligibility": "KEEP", "C_label": "C2", "S_label": "S2", "A_label": "A2"},
    {"eligibility": "REMOVE", "C_label": None, "S_label": None, "A_label": None, "remove_reason": ""},
    {"eligibility": "KEEP", "C_label": "C0", "S_label": "S0", "A_label": "A0", "uncertain": True},
])
def test_invalid_constraints(labels):
    with pytest.raises(ValidationError): validate_annotation(labels)
