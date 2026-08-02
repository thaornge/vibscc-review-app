# scripts/export_task07_bundle.py

import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

BASE_DIR = Path(__file__).resolve().parent.parent
MOCK_DATA_DIR = BASE_DIR / "mock_data"

load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

def export_task07_data():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Query tất cả case đã kết thúc
    res = client.table("review_routes") \
        .select("record_id, status, review_route, records(text_annotation), human_annotations(*), adjudications(*)") \
        .in_("status", ["RESOLVED_HUMAN_AGREEMENT", "ADJUDICATED"]) \
        .execute()

    data = res.data
    print(f"Tổng số bản ghi xuất ra: {len(data)}")

    os.makedirs("exports", exist_ok=True)
    out_file = "exports/FINAL_TASK07_BUNDLE.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Đã xuất file thành công tại: {out_file}")

if __name__ == "__main__":
    export_task07_data()