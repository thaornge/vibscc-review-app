# tests/test_import_export.py

import pytest
import os
from supabase import create_client

@pytest.fixture
def supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        pytest.skip("Chưa thiết lập SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def test_reconciliation_count(supabase_client):
    """Kiểm tra tổng số record nhập vào khớp với tổng số case trong review_routes."""
    records_count = supabase_client.table("records").select("record_id", count="exact").execute().count
    routes_count = supabase_client.table("review_routes").select("record_id", count="exact").execute().count
    
    assert records_count == routes_count, "Lỗi Reconciliation: Số lượng records và review_routes không bằng nhau!"

def test_blind_route_has_no_prediction_leakage(supabase_client):
    """Đảm bảo các record ở route DOUBLE_BLIND_TEST không chứa LLM predictions."""
    test_candidates = supabase_client.table("review_routes") \
        .select("record_id") \
        .eq("review_route", "DOUBLE_BLIND_TEST") \
        .execute().data

    record_ids = [r["record_id"] for r in test_candidates]
    if record_ids:
        preds = supabase_client.table("llm_predictions") \
            .select("id") \
            .in_("record_id", record_ids) \
            .execute().data
        assert len(preds) == 0, "Lỗi Rò rỉ: Dữ liệu TEST_RESERVE không được phép có LLM predictions!"