from concurrent.futures import ThreadPoolExecutor

import pytest

from src.mock_seed import build_mock_store
from src.repository_fake import FakeRepository
from src.review_service import ConflictError, ReviewService


def annotation(action="BLIND_LABEL", c="C0", s="S0", a="A0", note=""):
    return {"decision_action": action, "eligibility": "KEEP", "remove_reason": "", "C_label": c, "S_label": s, "A_label": a, "uncertain": False, "uncertainty_reason": "", "evidence": "mock evidence", "rule_id": "R1", "note": note, "guideline_version": "p1.0-mock"}


def repo(tmp_path):
    return FakeRepository(tmp_path / "state.json", build_mock_store)


def test_blind_view_has_no_prediction_route_reason_audit_or_other_human(tmp_path):
    service = ReviewService(repo(tmp_path))
    view = service.reviewer_view("ANN_03", "ASG_B002_1")
    serialized = repr(view)
    assert "llm_consensus" not in view
    assert "route_reason" not in serialized
    assert "audit_flag" not in serialized
    assert "predictions" not in serialized
    assert "ANN_04" not in serialized


def test_visible_view_exposes_only_consensus(tmp_path):
    service = ReviewService(repo(tmp_path))
    view = service.reviewer_view("ANN_01", "ASG_V001_1")
    assert view["llm_consensus"]["C_label"] == "C0"
    assert "model_slot" in view["llm_consensus"]


def test_draft_persists_after_repository_reopen(tmp_path):
    path = tmp_path / "state.json"
    first = ReviewService(FakeRepository(path, build_mock_store))
    version = first.save_draft("ANN_03", "ASG_B002_1", annotation(), 0)
    second = ReviewService(FakeRepository(path, build_mock_store))
    view = second.reviewer_view("ANN_03", "ASG_B002_1")
    assert version == 1
    assert view["draft"]["save_status"] == "DRAFT"
    assert view["draft"]["C_label"] == "C0"


def test_double_blind_agreement_resolves_and_locks_initial_rows(tmp_path):
    repository = repo(tmp_path)
    service = ReviewService(repository)
    assert service.submit("ANN_01", "ASG_A001_1", annotation(), 0) == "WAITING_SECOND_REVIEW"
    assert service.submit("ANN_02", "ASG_A001_2", annotation(), 0) == "RESOLVED_HUMAN_AGREEMENT"
    with pytest.raises(ConflictError):
        service.submit("ANN_01", "ASG_A001_1", annotation(), 1)


def test_visible_accept_requires_exact_consensus_and_edit_requires_note(tmp_path):
    service = ReviewService(repo(tmp_path))
    assert service.submit("ANN_01", "ASG_V001_1", annotation("ACCEPT"), 0) == "RESOLVED_VISIBLE_ACCEPT"
    with pytest.raises(Exception):
        service.submit("ANN_03", "ASG_V002_1", annotation("EDIT", "C1", "S2", "A3"), 0)
    assert service.submit("ANN_03", "ASG_V002_1", annotation("EDIT", "C1", "S2", "A3", "Human correction"), 0) == "RESOLVED_VISIBLE_EDIT"


def test_concurrent_submit_does_not_overwrite(tmp_path):
    service = ReviewService(repo(tmp_path))
    def submit_once():
        try:
            return service.submit("ANN_03", "ASG_I001_1", annotation(), 0)
        except ConflictError:
            return "CONFLICT"
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: submit_once(), range(2)))
    assert sorted(outcomes) == ["CONFLICT", "WAITING_SECOND_REVIEW"]
    data = service.repository.snapshot()
    assert list(data["annotations"]).count("ASG_I001_1") == 1


def test_test_reserve_has_no_predictions_and_still_reviews(tmp_path):
    repository = repo(tmp_path)
    service = ReviewService(repository)
    assert "T001" not in repository.snapshot()["predictions"]
    assert service.submit("ANN_01", "ASG_T001_1", annotation(), 0) == "WAITING_SECOND_REVIEW"
    assert service.submit("ANN_02", "ASG_T001_2", annotation(), 0) == "RESOLVED_HUMAN_AGREEMENT"
