import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from supabase import create_client

from src.repository_supabase import SupabaseRepository
from src.ui_supabase import normalize_initial
from src.validators import ValidationError


load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)


class FakeResponse:
    def __init__(self, data=None, count=None):
        self.data = data or []
        self.count = count


class FakeTable:
    def __init__(self, client, name):
        self.client = client
        self.name = name
        self.action = None
        self.filters = []
        self.payload = None

    def delete(self):
        self.action = "delete"
        return self

    def insert(self, payload):
        self.action = "insert"
        self.payload = payload
        return self

    def in_(self, column, values):
        self.filters.append((column, tuple(values)))
        return self

    def execute(self):
        self.client.calls.append((self.name, self.action, self.filters, self.payload))
        return FakeResponse(self.payload if self.action == "insert" else [])


class FakeClient:
    def __init__(self):
        self.calls = []

    def table(self, name):
        return FakeTable(self, name)


@pytest.fixture
def supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        pytest.skip("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is not configured")
    return create_client(url, key)


def test_reconciliation_count(supabase_client):
    records_count = supabase_client.table("records").select("record_id", count="exact").execute().count
    routes_count = supabase_client.table("review_routes").select("record_id", count="exact").execute().count

    assert records_count == routes_count, "records and review_routes counts must match"


def test_blind_route_has_no_prediction_leakage(supabase_client):
    test_candidates = supabase_client.table("review_routes") \
        .select("record_id") \
        .eq("review_route", "DOUBLE_BLIND_TEST") \
        .execute().data

    record_ids = [row["record_id"] for row in test_candidates]
    if record_ids:
        preds = supabase_client.table("llm_predictions") \
            .select("id") \
            .in_("record_id", record_ids) \
            .execute().data
        assert len(preds) == 0, "TEST_RESERVE records must not have LLM predictions"


def test_import_predictions_replaces_bundle_scope_before_insert():
    repo = SupabaseRepository.__new__(SupabaseRepository)
    repo.client = FakeClient()
    predictions = [
        {"record_id": "R1", "run_id": "RUN1", "model_slot": 1},
        {"record_id": "R1", "run_id": "RUN1", "model_slot": 2},
        {"record_id": "R2", "run_id": "RUN1", "model_slot": 1},
    ]

    response = repo._replace_predictions_for_import(predictions)

    assert response.data == predictions
    assert repo.client.calls[0] == (
        "llm_predictions",
        "delete",
        [("record_id", ("R1", "R2")), ("run_id", ("RUN1",))],
        None,
    )
    assert repo.client.calls[1] == ("llm_predictions", "insert", [], predictions)


def test_normalize_initial_reads_discussion_proposal_fields():
    labels = normalize_initial({
        "proposed_eligibility": "REMOVE",
        "proposed_c": None,
        "proposed_s": None,
        "proposed_a": None,
        "remove_reason": "OTHER_REMOVE",
    })

    assert labels["eligibility"] == "REMOVE"
    assert labels["C_label"] == "C0"
    assert labels["S_label"] == "S0"
    assert labels["A_label"] == "A0"


def test_supabase_repository_rejects_invalid_submit_before_write():
    repo = SupabaseRepository.__new__(SupabaseRepository)
    repo.client = FakeClient()

    with pytest.raises(ValidationError):
        repo.submit_annotation(assignment_id=1, annotation_data={
            "decision_action": "BLIND_LABEL",
            "record_id": "R1",
            "annotator_code": "ANN_01",
            "eligibility": "KEEP",
            "c_label": "C0",
            "s_label": "S2",
            "a_label": "A0",
            "guideline_version": "p1.0",
        })

    assert repo.client.calls == []
