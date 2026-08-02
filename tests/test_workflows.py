import pytest
from src.constants import CaseStatus
from src.repository_fake import RepositoryError


def test_draft_persists_after_new_repository_instance(repo, c1):
    repo.save_draft("CASE_BLIND_001", "reviewer_1", c1)
    reloaded = type(repo)(state_path=repo.state_path)
    view = reloaded.case_for_reviewer("CASE_BLIND_001", "reviewer_1")
    assert view["assignment"]["draft"]["C_label"] == "C1"


def test_duplicate_submit_is_blocked(repo, c0):
    repo.submit("CASE_VISIBLE_001", "reviewer_1", c0, "ACCEPT")
    with pytest.raises(RepositoryError): repo.submit("CASE_VISIBLE_001", "reviewer_1", c0, "ACCEPT")


def test_two_equal_blind_labels_resolve(repo, c1):
    repo.submit("CASE_BLIND_001", "reviewer_1", c1, "BLIND_LABEL")
    repo.submit("CASE_BLIND_001", "reviewer_2", c1, "BLIND_LABEL")
    assert repo._case("CASE_BLIND_001")["status"] == CaseStatus.RESOLVED_HUMAN_AGREEMENT


def test_disagreement_discussion_confirm(repo, c1):
    other = {**c1, "S_label": "S4"}
    repo.submit("CASE_BLIND_001", "reviewer_1", c1, "BLIND_LABEL")
    repo.submit("CASE_BLIND_001", "reviewer_2", other, "BLIND_LABEL")
    assert repo._case("CASE_BLIND_001")["status"] == CaseStatus.DISCUSSION_REQUIRED
    repo.propose("CASE_BLIND_001", "reviewer_1", c1, "Theo rule 3.2")
    repo.respond("CASE_BLIND_001", "reviewer_2", True, "Đồng ý sau thảo luận")
    assert repo._case("CASE_BLIND_001")["status"] == CaseStatus.RESOLVED_DISCUSSION


def test_disagreement_reject_then_admin_adjudicates(repo, c1):
    other = {**c1, "S_label": "S4"}
    repo.submit("CASE_BLIND_001", "reviewer_1", c1, "BLIND_LABEL")
    repo.submit("CASE_BLIND_001", "reviewer_2", other, "BLIND_LABEL")
    repo.propose("CASE_BLIND_001", "reviewer_1", c1, "Proposal")
    repo.respond("CASE_BLIND_001", "reviewer_2", False, "Chưa đồng ý")
    repo.adjudicate("CASE_BLIND_001", "admin_phuc", c1, "Quyết định theo guideline")
    assert repo._case("CASE_BLIND_001")["status"] == CaseStatus.RESOLVED_ADJUDICATION


def test_non_admin_cannot_adjudicate(repo, c1):
    with pytest.raises(RepositoryError): repo.adjudicate("CASE_ADJ_001", "reviewer_1", c1, "No")


def test_visible_accept_and_edit(repo, c0):
    repo.submit("CASE_VISIBLE_001", "reviewer_1", c0, "ACCEPT")
    assert repo._case("CASE_VISIBLE_001")["status"] == CaseStatus.RESOLVED_VISIBLE_ACCEPT
