def test_blind_view_hides_llm_audit_and_other_reviewer(repo):
    view = repo.case_for_reviewer("CASE_BLIND_001", "reviewer_1")
    serialized = str(view)
    assert "private_prediction_fixture" not in serialized
    assert "llm_consensus" not in serialized
    assert "audit_flag" not in serialized
    assert "reviewer_2" not in serialized


def test_audit_route_does_not_reveal_audit_flag(repo):
    view = repo.case_for_reviewer("CASE_AUDIT_001", "reviewer_2")
    assert "audit_flag" not in view
    assert "llm_consensus" not in view


def test_test_reserve_works_without_predictions(repo):
    view = repo.case_for_reviewer("CASE_TEST_001", "reviewer_3")
    assert view["route"] == "DOUBLE_BLIND_TEST"
    assert "llm_consensus" not in view
