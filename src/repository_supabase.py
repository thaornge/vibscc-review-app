# src/repository_supabase.py

import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from src.repository_base import RepositoryBase
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class SupabaseRepository(RepositoryBase):
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        url = supabase_url or os.getenv("SUPABASE_URL", "")
        key = supabase_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_KEY", "")
        if not url or not key:
            raise ValueError("Thiếu cấu hình SUPABASE_URL hoặc SUPABASE_KEY trong file .env")
        self.client: Client = create_client(url, key)

    def get_assigned_cases_for_user(self, annotator_code: str) -> List[Dict[str, Any]]:
        # 1. Query danh sách assignments kèm thông tin record liên quan
        response = self.client.table("assignments") \
            .select("*, records!inner(*)") \
            .eq("annotator_code", annotator_code) \
            .execute()
        
        assignments = response.data or []
        if not assignments:
            return []

        # 2. Lấy danh sách record_id để query thêm thông tin review_routes tương ứng
        record_ids = [a["record_id"] for a in assignments if "record_id" in a]
        
        if record_ids:
            routes_res = self.client.table("review_routes") \
                .select("*") \
                .in_("record_id", record_ids) \
                .execute()
            
            # Map thông tin review_routes vào từng assignment theo record_id
            routes_map = {r["record_id"]: r for r in (routes_res.data or [])}
            for a in assignments:
                a["review_routes"] = routes_map.get(a["record_id"], {})

        return assignments

    def save_draft(self, assignment_id: int, annotation_data: Dict[str, Any]) -> bool:
        data = {**annotation_data, "assignment_id": assignment_id, "is_draft": True}
        
        # Loại bỏ decision_action nếu schema Supabase chưa có cột này để tránh lỗi PGRST204
        data.pop("decision_action", None)
        
        response = self.client.table("human_annotations") \
            .upsert(data, on_conflict="assignment_id") \
            .execute()
        
        self.client.table("assignments").update({"status": "DRAFT"}).eq("assignment_id", assignment_id).execute()
        return bool(response.data)

    def submit_annotation(self, assignment_id: int, annotation_data: Dict[str, Any]) -> Dict[str, Any]:
        data = {
            **annotation_data, 
            "assignment_id": assignment_id, 
            "is_draft": False, 
            "submitted_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        # Loại bỏ decision_action nếu schema Supabase chưa có cột này để tránh lỗi PGRST204
        data.pop("decision_action", None)
        
        # 1. Lưu nhãn chính thức
        res = self.client.table("human_annotations").upsert(data, on_conflict="assignment_id").execute()
        
        # 2. Cập nhật trạng thái assignment thành SUBMITTED
        self.client.table("assignments").update({"status": "SUBMITTED"}).eq("assignment_id", assignment_id).execute()
        
        # 3. Kích hoạt kiểm tra xem cả 2 humans đã submit chưa để đổi status của case
        # (Xử lý đối soát 2 human agreement / disagreement)
        self._reconcile_case_status(annotation_data.get("record_id"))
        
        return res.data[0] if res.data else {}

    def _reconcile_case_status(self, record_id: str):
        # Lấy tất cả submitted annotations cho record_id này
        ann_res = self.client.table("human_annotations") \
            .select("*") \
            .eq("record_id", record_id) \
            .eq("is_draft", False) \
            .execute()
        
        annotations = ann_res.data
        route_res = self.client.table("review_routes").select("*").eq("record_id", record_id).execute()
        if not route_res.data:
            return
        
        route_info = route_res.data[0]
        req_humans = route_info["required_humans"]

        if len(annotations) == req_humans:
            if req_humans == 1:
                new_status = "RESOLVED_HUMAN_AGREEMENT"
            else:
                ann1, ann2 = annotations[0], annotations[1]
                match = (
                    ann1["eligibility"] == ann2["eligibility"] and
                    ann1["c_label"] == ann2["c_label"] and
                    ann1["s_label"] == ann2["s_label"] and
                    ann1["a_label"] == ann2["a_label"]
                )
                new_status = "RESOLVED_HUMAN_AGREEMENT" if match else "DISCUSSION_REQUIRED"

            self.client.table("review_routes").update({"status": new_status}).eq("record_id", record_id).execute()

    def get_discussion_cases(self, annotator_code: str) -> List[Dict[str, Any]]:
        # 1. Query danh sách review_routes có status DISCUSSION_REQUIRED kèm records
        res = self.client.table("review_routes") \
            .select("*, records(*)") \
            .eq("status", "DISCUSSION_REQUIRED") \
            .execute()
        
        routes = res.data or []
        if not routes:
            return []

        record_ids = [r["record_id"] for r in routes if "record_id" in r]

        if record_ids:
            # 2. Query human_annotations và discussions theo record_id
            ann_res = self.client.table("human_annotations").select("*").in_("record_id", record_ids).execute()
            disc_res = self.client.table("discussions").select("*").in_("record_id", record_ids).execute()

            # Gom nhóm data theo record_id
            anns_map = {}
            for ann in (ann_res.data or []):
                anns_map.setdefault(ann["record_id"], []).append(ann)

            discs_map = {}
            for disc in (disc_res.data or []):
                discs_map.setdefault(disc["record_id"], []).append(disc)

            # Map dữ liệu ngược lại vào danh sách routes
            for r in routes:
                rec_id = r["record_id"]
                r["human_annotations"] = anns_map.get(rec_id, [])
                r["discussions"] = discs_map.get(rec_id, [])

        return routes

    def submit_proposal(self, record_id: str, proposer_code: str, proposal: Dict[str, Any]) -> bool:
        data = {
            "record_id": record_id,
            "proposer_code": proposer_code,
            **proposal,
            "status": "OPEN"
        }
        res = self.client.table("discussions").insert(data).execute()
        return bool(res.data)

    def resolve_discussion(self, discussion_id: int, responder_code: str, action: str) -> bool:
        if action == "ACCEPT":
            # Chấp nhận đề xuất -> Case chốt
            disc = self.client.table("discussions").select("*").eq("discussion_id", discussion_id).execute().data[0]
            self.client.table("discussions").update({"status": "ACCEPTED", "resolved_at": datetime.datetime.now().isoformat()}).eq("discussion_id", discussion_id).execute()
            self.client.table("review_routes").update({"status": "RESOLVED_HUMAN_AGREEMENT"}).eq("record_id", disc["record_id"]).execute()
        else:
            # Bác bỏ đề xuất -> Leo thang lên Adjudication
            disc = self.client.table("discussions").select("*").eq("discussion_id", discussion_id).execute().data[0]
            self.client.table("discussions").update({"status": "REJECTED", "resolved_at": datetime.datetime.now().isoformat()}).eq("discussion_id", discussion_id).execute()
            self.client.table("review_routes").update({"status": "ADJUDICATION_REQUIRED"}).eq("record_id", disc["record_id"]).execute()
        return True

    def get_adjudication_cases(self) -> List[Dict[str, Any]]:
        # 1. Query danh sách review_routes có status ADJUDICATION_REQUIRED kèm records
        res = self.client.table("review_routes") \
            .select("*, records(*)") \
            .eq("status", "ADJUDICATION_REQUIRED") \
            .execute()
        
        routes = res.data or []
        if not routes:
            return []

        record_ids = [r["record_id"] for r in routes if "record_id" in r]

        if record_ids:
            # 2. Query human_annotations và discussions theo record_id
            ann_res = self.client.table("human_annotations").select("*").in_("record_id", record_ids).execute()
            disc_res = self.client.table("discussions").select("*").in_("record_id", record_ids).execute()

            # Gom nhóm data theo record_id
            anns_map = {}
            for ann in (ann_res.data or []):
                anns_map.setdefault(ann["record_id"], []).append(ann)

            discs_map = {}
            for disc in (disc_res.data or []):
                discs_map.setdefault(disc["record_id"], []).append(disc)

            # Máp dữ liệu ngược lại vào danh sách routes
            for r in routes:
                rec_id = r["record_id"]
                r["human_annotations"] = anns_map.get(rec_id, [])
                r["discussions"] = discs_map.get(rec_id, [])

        return routes

    def submit_adjudication(self, record_id: str, admin_code: str, final_data: Dict[str, Any]) -> bool:
        data = {
            "record_id": record_id,
            "adjudicator_code": admin_code,
            **final_data
        }
        self.client.table("adjudications").insert(data).execute()
        self.client.table("review_routes").update({"status": "ADJUDICATED"}).eq("record_id", record_id).execute()
        return True

    def import_task06_bundle(self, records: List[Dict], predictions: List[Dict], routes: List[Dict]) -> Dict[str, int]:
        r_res = self.client.table("records").upsert(records, on_conflict="record_id").execute()
        p_res = self.client.table("llm_predictions").insert(predictions).execute()
        rt_res = self.client.table("review_routes").upsert(routes, on_conflict="record_id").execute()
        return {
            "records": len(r_res.data or []),
            "predictions": len(p_res.data or []),
            "routes": len(rt_res.data or [])
        }

    def export_task07_bundle(self) -> Dict[str, Any]:
        records = self.client.table("records").select("*, review_routes(*), human_annotations(*), adjudications(*)").execute()
        return {"export_timestamp": datetime.datetime.now().isoformat(), "data": records.data}