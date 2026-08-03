import pytest

from src.adjudication_service import AdjudicationService
from src.constants import CaseStatus
from src.discussion_service import DiscussionService
from src.mock_seed import build_mock_store
from src.repository_fake import FakeRepository
from src.review_service import ConflictError, ReviewService


def annotation(action="BLIND_LABEL", c="C1", s="S2", a="A3", note=""):
    return {
        "decision_action": action,
        "eligibility": "KEEP",
        "remove_reason": "",
        "C_label": c,
        "S_label": s,
        "A_label": a,
        "uncertain": False,
        "uncertainty_reason": "",
        "evidence": "mock evidence",
        "rule_id": "R1",
        "note": note,
        "guideline_version": "p1.0-mock",
    }


def repo(tmp_path):
    return FakeRepository(tmp_path / "state.json", build_mock_store)


def case_status(repository, case_id):
    return repository.snapshot()["cases"][case_id]["case_status"]


def test_draft_persists_after_new_repository_instance(tmp_path):
    path = tmp_path / "state.json"
    service = ReviewService(FakeRepository(path, build_mock_store))
    service.save_draft("ANN_03", "ASG_B002_1", annotation(), 0)
    reloaded = ReviewService(FakeRepository(path, build_mock_store))
    view = reloaded.reviewer_view("ANN_03", "ASG_B002_1")
    assert view["draft"]["C_label"] == "C1"


def test_duplicate_submit_is_blocked(tmp_path):
    service = ReviewService(repo(tmp_path))
    service.submit("ANN_01", "ASG_V001_1", annotation("ACCEPT", "C0", "S0", "A0"), 0)
    with pytest.raises(ConflictError):
        service.submit("ANN_01", "ASG_V001_1", annotation("ACCEPT", "C0", "S0", "A0"), 1)


def test_two_equal_blind_labels_resolve(tmp_path):
    repository = repo(tmp_path)
    service = ReviewService(repository)
    service.submit("ANN_01", "ASG_A001_1", annotation(), 0)
    service.submit("ANN_02", "ASG_A001_2", annotation(), 0)
    assert case_status(repository, "CASE_A001") == CaseStatus.RESOLVED_HUMAN_AGREEMENT


def test_disagreement_discussion_confirm(tmp_path):
    repository = repo(tmp_path)
    reviews = ReviewService(repository)
    discussions = DiscussionService(repository)
    reviews.submit("ANN_03", "ASG_B002_1", annotation(), 0)
    reviews.submit("ANN_04", "ASG_B002_2", annotation(c="C1", s="S4", a="A3"), 0)
    assert case_status(repository, "CASE_B002") == CaseStatus.DISCUSSION_REQUIRED
    discussions.propose("ANN_03", "CASE_B002", annotation(), "Use rule R1")
    discussions.respond("ANN_04", "CASE_B002", True, "Agree after discussion")
    assert case_status(repository, "CASE_B002") == CaseStatus.RESOLVED_DISCUSSION


def test_disagreement_reject_then_admin_adjudicates(tmp_path):
    repository = repo(tmp_path)
    reviews = ReviewService(repository)
    discussions = DiscussionService(repository)
    adjudications = AdjudicationService(repository)
    reviews.submit("ANN_03", "ASG_B002_1", annotation(), 0)
    reviews.submit("ANN_04", "ASG_B002_2", annotation(c="C1", s="S4", a="A3"), 0)
    discussions.propose("ANN_03", "CASE_B002", annotation(), "Proposal")
    discussions.respond("ANN_04", "CASE_B002", False, "Disagree")
    adjudications.resolve("ADMIN_PHUC", "CASE_B002", annotation(), "Final decision")
    assert case_status(repository, "CASE_B002") == CaseStatus.RESOLVED_ADJUDICATION


def test_non_admin_cannot_adjudicate(tmp_path):
    with pytest.raises(PermissionError):
        AdjudicationService(repo(tmp_path)).resolve("ANN_01", "CASE_T002", annotation(), "No")


def test_visible_accept_and_edit(tmp_path):
    repository = repo(tmp_path)
    service = ReviewService(repository)
    service.submit("ANN_01", "ASG_V001_1", annotation("ACCEPT", "C0", "S0", "A0"), 0)
    assert case_status(repository, "CASE_V001") == CaseStatus.RESOLVED_VISIBLE_ACCEPT
