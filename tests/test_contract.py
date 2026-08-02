from src.mock_seed import build_mock_store


def test_assignment_and_route_integrity():
    data = build_mock_store()
    for case in data["cases"].values():
        assignments = [a for a in data["assignments"].values() if a["case_id"] == case["case_id"]]
        assert len(assignments) == case["required_reviews"]
        assert len({a["review_slot"] for a in assignments}) == len(assignments)
        assert len({a["reviewer_id"] for a in assignments}) == len(assignments)
        if case["review_route"] == "SINGLE_VISIBLE_REVIEW":
            assert case["required_reviews"] == 1
            assert {a["visibility_mode"] for a in assignments} == {"VISIBLE"}
        else:
            assert case["required_reviews"] == 2
            assert {a["visibility_mode"] for a in assignments} == {"BLIND"}


def test_mock_coverage_has_all_required_scenarios():
    data = build_mock_store()
    routes = {case["review_route"] for case in data["cases"].values()}
    reasons = {case["route_reason"] for case in data["cases"].values()}
    assert routes == {"DOUBLE_BLIND", "DOUBLE_BLIND_AUDIT", "SINGLE_VISIBLE_REVIEW", "DOUBLE_BLIND_TEST"}
    assert {"DISAGREEMENT_C", "LLM_UNCERTAIN", "INVALID_PREDICTION", "AUDIT", "CONSENSUS", "TEST_RESERVE"} <= reasons
    assert data["cases"]["CASE_B001"]["case_status"] == "DISCUSSION_REQUIRED"
    assert data["cases"]["CASE_T002"]["case_status"] == "ADJUDICATION_REQUIRED"

