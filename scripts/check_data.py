import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

print("=== 1. DANH SÁCH USERS ===")
res_users = supabase.table("users").select("*").execute()
for u in res_users.data:
    print(u)

print("\n=== 2. MẪU 3 RECORDS ĐẦU TIÊN ===")
res_records = supabase.table("records").select("record_id, text_annotation, batch_id").limit(3).execute()
for r in res_records.data:
    print(r)

print("\n=== 3. THỐNG KÊ SỐ LƯỢNG DÒNG MỖI BẢNG ===")
for table in ["users", "records", "llm_predictions", "review_routes", "assignments"]:
    count_res = supabase.table(table).select("*", count="exact").execute()
    print(f"- Bảng {table}: {count_res.count} dòng")