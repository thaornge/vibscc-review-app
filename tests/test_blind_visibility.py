from src.mock_seed import build_mock_store
from src.repository_fake import FakeRepository
from src.review_service import ReviewService


def repo(tmp_path):
    return FakeRepository(tmp_path / "state.json", build_mock_store)


def test_blind_view_hides_llm_audit_and_other_reviewer(tmp_path):
    view = ReviewService(repo(tmp_path)).reviewer_view("ANN_03", "ASG_B002_1")
    serialized = str(view)
    assert "private_prediction_fixture" not in serialized
    assert "llm_consensus" not in serialized
    assert "audit_flag" not in serialized
    assert "ANN_04" not in serialized


def test_audit_route_does_not_reveal_audit_flag(tmp_path):
    view = ReviewService(repo(tmp_path)).reviewer_view("ANN_01", "ASG_A001_1")
    assert "audit_flag" not in view
    assert "llm_consensus" not in view


def test_test_reserve_works_without_predictions(tmp_path):
    view = ReviewService(repo(tmp_path)).reviewer_view("ANN_01", "ASG_T001_1")
    assert view["visibility_mode"] == "BLIND"
    assert "llm_consensus" not in view
