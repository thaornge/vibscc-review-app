# scripts/import_task06_bundle.py

import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

BASE_DIR = Path(__file__).resolve().parent.parent
MOCK_DATA_DIR = BASE_DIR / "mock_data"

load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

def clean_dataframe(df: pd.DataFrame) -> list:
    """
    1. Chuyển tên cột sang chữ thường để khớp chuẩn PostgreSQL
    2. Chuyển giá trị NaN của pandas thành None chuẩn JSON
    """
    df_clean = df.copy()
    df_clean.columns = [col.lower() for col in df_clean.columns]
    return df_clean.where(pd.notnull(df_clean), None).to_dict(orient="records")

def replace_predictions(client, predictions_data: list):
    if not predictions_data:
        return
    record_ids = sorted({row["record_id"] for row in predictions_data if row.get("record_id")})
    run_ids = sorted({row["run_id"] for row in predictions_data if row.get("run_id")})
    query = client.table("llm_predictions").delete()
    if record_ids:
        query = query.in_("record_id", record_ids)
    if run_ids:
        query = query.in_("run_id", run_ids)
    query.execute()
    client.table("llm_predictions").insert(predictions_data).execute()

def import_task06_data():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Lỗi: Chưa cấu hình biến môi trường SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY.")
        return

    print("Đã tìm thấy API Key! Đang kết nối tới Supabase...")
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("--- 1. Import Users ---")
    users_df = pd.read_csv(MOCK_DATA_DIR / "mock_users.csv")
    users_data = clean_dataframe(users_df)
    client.table("users").upsert(users_data, on_conflict="annotator_code").execute()

    print("--- 2. Import Records ---")
    records_df = pd.read_csv(MOCK_DATA_DIR / "llm_input_pool_mock.csv")
    records_data = clean_dataframe(records_df)
    client.table("records").upsert(records_data, on_conflict="record_id").execute()

    print("--- 3. Import LLM Predictions ---")
    preds_df = pd.read_csv(MOCK_DATA_DIR / "llm_predictions_long_mock.csv")
    preds_data = clean_dataframe(preds_df)
    replace_predictions(client, preds_data)

    print("--- 4. Import Review Routes ---")
    routes_df = pd.read_csv(MOCK_DATA_DIR / "review_routes_mock.csv")
    routes_data = clean_dataframe(routes_df)
    client.table("review_routes").upsert(routes_data, on_conflict="record_id").execute()

    print("--- 5. Auto Generating Assignments ---")
    annotators = ['ANN_01', 'ANN_02', 'ANN_03', 'ANN_04']
    assignments = []
    
    for idx, row in routes_df.iterrows():
        req = int(row['required_humans'])
        rec_id = row['record_id']
        a1 = annotators[idx % 4]
        assignments.append({"record_id": rec_id, "annotator_code": a1, "slot_index": 1})
        if req == 2:
            a2 = annotators[(idx + 1) % 4]
            assignments.append({"record_id": rec_id, "annotator_code": a2, "slot_index": 2})

    client.table("assignments").upsert(assignments, on_conflict="record_id,annotator_code").execute()
    print(" Import Task 06 Bundle hoàn tất thành công 100%!")

if __name__ == "__main__":
    import_task06_data()
