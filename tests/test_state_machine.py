import pytest
from src.constants import CaseStatus
from src.state_machine import InvalidTransition, assert_transition


def test_valid_transition():
    assert_transition(CaseStatus.ASSIGNED, CaseStatus.IN_REVIEW)


def test_invalid_transition():
    with pytest.raises(InvalidTransition):
        assert_transition(CaseStatus.ASSIGNED, CaseStatus.RESOLVED_ADJUDICATION)
