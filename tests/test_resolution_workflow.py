from src.adjudication_service import AdjudicationService
from src.discussion_service import DiscussionService
from src.mock_seed import build_mock_store
from src.repository_fake import FakeRepository


def proposal(c="C1", s="S2", a="A3"):
    return {"eligibility": "KEEP", "remove_reason": "", "C_label": c, "S_label": s, "A_label": a, "uncertain": False, "uncertainty_reason": "", "evidence": "proposal evidence", "rule_id": "R2", "note": "", "guideline_version": "p1.0-mock"}


def test_discussion_confirm_and_escalation_then_adjudication(tmp_path):
    repository = FakeRepository(tmp_path / "state.json", build_mock_store)
    discussions = DiscussionService(repository)
    discussions.propose("ANN_01", "CASE_B001", proposal(), "Use rule R2")
    assert discussions.respond("ANN_02", "CASE_B001", True) == "RESOLVED_DISCUSSION"

    pending = AdjudicationService(repository).list_pending("ADMIN_PHUC")
    assert {item["case"]["case_id"] for item in pending} == {"CASE_T002"}
    AdjudicationService(repository).resolve("ADMIN_PHUC", "CASE_T002", proposal("C2", "S0", "A5"), "Admin applies rule R5")
    data = repository.snapshot()
    assert data["cases"]["CASE_T002"]["case_status"] == "RESOLVED_ADJUDICATION"
    assert data["adjudications"]["CASE_T002"]["adjudicator_code"] == "ADMIN_PHUC"

