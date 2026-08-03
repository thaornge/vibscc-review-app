# src/repository_supabase.py

import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from src.repository_base import RepositoryBase
from src.validators import validate_annotation
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

    def _clean_annotation_payload(self, annotation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Chỉ giữ lại các cột thực sự tồn tại trong schema bảng human_annotations."""
        valid_columns = {
            "assignment_id", "record_id", "annotator_code", 
            "eligibility", "c_label", "s_label", "a_label", 
            "remove_reason", "uncertain", "uncertainty_reason",
            "evidence", "rule_id", "note", "guideline_version",
            "is_draft", "submitted_at"
        }
        return {k: v for k, v in annotation_data.items() if k in valid_columns}

    def _annotation_for_validation(self, annotation_data: Dict[str, Any], decision_action: str = "BLIND_LABEL") -> Dict[str, Any]:
        return {
            "decision_action": annotation_data.get("decision_action") or decision_action,
            "eligibility": annotation_data.get("eligibility"),
            "remove_reason": annotation_data.get("remove_reason") or "",
            "C_label": annotation_data.get("C_label") or annotation_data.get("c_label"),
            "S_label": annotation_data.get("S_label") or annotation_data.get("s_label"),
            "A_label": annotation_data.get("A_label") or annotation_data.get("a_label"),
            "uncertain": annotation_data.get("uncertain") in {True, "YES", "yes", "true", "TRUE"},
            "uncertainty_reason": annotation_data.get("uncertainty_reason") or "",
            "evidence": annotation_data.get("evidence") or "",
            "rule_id": annotation_data.get("rule_id") or "",
            "note": annotation_data.get("note") or "",
            "guideline_version": annotation_data.get("guideline_version") or "",
        }
    
    def save_draft(self, assignment_id: int, annotation_data: Dict[str, Any]) -> bool:
        data = {**annotation_data, "assignment_id": assignment_id, "is_draft": True}
        clean_data = self._clean_annotation_payload(data)
        
        # 1. Kiểm tra xem đã có bản ghi draft/annotation nào cho assignment_id này chưa
        existing = self.client.table("human_annotations").select("annotation_id").eq("assignment_id", assignment_id).execute()
        
        if existing.data:
            # Nếu đã tồn tại -> Update
            response = self.client.table("human_annotations") \
                .update(clean_data) \
                .eq("assignment_id", assignment_id) \
                .execute()
        else:
            # Nếu chưa có -> Insert
            response = self.client.table("human_annotations") \
                .insert(clean_data) \
                .execute()
        
        self.client.table("assignments").update({"status": "DRAFT"}).eq("assignment_id", assignment_id).execute()
        return bool(response.data)

    def submit_annotation(self, assignment_id: int, annotation_data: Dict[str, Any]) -> Dict[str, Any]:
        validate_annotation(self._annotation_for_validation(annotation_data))
        data = {
            **annotation_data, 
            "assignment_id": assignment_id, 
            "is_draft": False, 
            "submitted_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        clean_data = self._clean_annotation_payload(data)

        # 1. Kiểm tra xem đã có bản ghi cho assignment_id này chưa
        existing = self.client.table("human_annotations").select("annotation_id").eq("assignment_id", assignment_id).execute()
        
        if existing.data:
            # Nếu đã tồn tại -> Update
            res = self.client.table("human_annotations") \
                .update(clean_data) \
                .eq("assignment_id", assignment_id) \
                .execute()
        else:
            # Nếu chưa có -> Insert
            res = self.client.table("human_annotations") \
                .insert(clean_data) \
                .execute()
        
        # 2. Cập nhật trạng thái assignment thành SUBMITTED
        self.client.table("assignments").update({"status": "SUBMITTED"}).eq("assignment_id", assignment_id).execute()
        
        # 3. Kích hoạt kiểm tra xem cả 2 humans đã submit chưa để đổi status của case
        self._reconcile_case_status(annotation_data.get("record_id"))
        
        return res.data[0] if res.data else {}

    def _reconcile_case_status(self, record_id: str):
        # Lấy tất cả submitted annotations cho record_id này
        ann_res = self.client.table("human_annotations") \
            .select("*") \
            .eq("record_id", record_id) \
            .eq("is_draft", False) \
            .execute()
        
        annotations = ann_res.data or []
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
                    ann1.get("eligibility") == ann2.get("eligibility") and
                    ann1.get("c_label") == ann2.get("c_label") and
                    ann1.get("s_label") == ann2.get("s_label") and
                    ann1.get("a_label") == ann2.get("a_label")
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

    def _clean_discussion_payload(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Chỉ giữ lại các cột thuộc bảng discussions."""
        payload = {**proposal}
        payload["proposed_eligibility"] = payload.get("proposed_eligibility") or payload.get("eligibility")
        payload["proposed_c"] = payload.get("proposed_c") or payload.get("c_label")
        payload["proposed_s"] = payload.get("proposed_s") or payload.get("s_label")
        payload["proposed_a"] = payload.get("proposed_a") or payload.get("a_label")
        payload["reason"] = payload.get("reason") or payload.get("rationale")
        valid_columns = {
            "record_id", "proposer_code", "proposed_eligibility", 
            "proposed_c", "proposed_s", "proposed_a", "reason", "status"
        }
        return {k: v for k, v in payload.items() if k in valid_columns}

    def submit_proposal(self, record_id: str, proposer_code: str, proposal: Dict[str, Any]) -> bool:
        validate_annotation(self._annotation_for_validation(proposal, "BLIND_LABEL"))
        data = {
            "record_id": record_id,
            "proposer_code": proposer_code,
            **proposal,
            "status": "OPEN"
        }
        clean_data = self._clean_discussion_payload(data)
        res = self.client.table("discussions").insert(clean_data).execute()
        return bool(res.data)

    def resolve_discussion(self, discussion_id: int, responder_code: str, action: str) -> bool:
        disc_res = self.client.table("discussions").select("*").eq("discussion_id", discussion_id).execute()
        if not disc_res.data:
            return False
        
        disc = disc_res.data[0]
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if action == "ACCEPT":
            # Chấp nhận đề xuất -> Case chốt
            self.client.table("discussions").update({"status": "ACCEPTED", "resolved_at": now_str}).eq("discussion_id", discussion_id).execute()
            self.client.table("review_routes").update({"status": "RESOLVED_HUMAN_AGREEMENT"}).eq("record_id", disc["record_id"]).execute()
        else:
            # Bác bỏ đề xuất -> Leo thang lên Adjudication
            self.client.table("discussions").update({"status": "REJECTED", "resolved_at": now_str}).eq("discussion_id", discussion_id).execute()
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

            # Map dữ liệu ngược lại vào danh sách routes
            for r in routes:
                rec_id = r["record_id"]
                r["human_annotations"] = anns_map.get(rec_id, [])
                r["discussions"] = discs_map.get(rec_id, [])

        return routes

    def _clean_adjudication_payload(self, final_data: Dict[str, Any]) -> Dict[str, Any]:
        """Chỉ giữ lại các cột thuộc bảng adjudications và map rationale/notes sang reasoning."""
        payload = {**final_data}
        
        # Tự động map rationale hoặc notes sang reasoning nếu DB yêu cầu cột reasoning (NOT NULL)
        reasoning_val = payload.get("reasoning") or payload.get("rationale") or payload.get("notes") or ""
        payload["reasoning"] = reasoning_val
        
        valid_columns = {
            "record_id", "adjudicator_code", "final_eligibility", 
            "final_c", "final_s", "final_a", "reasoning", "notes"
        }
        return {k: v for k, v in payload.items() if k in valid_columns}

    def submit_adjudication(self, record_id: str, admin_code: str, final_data: Dict[str, Any]) -> bool:
        validate_annotation({
            "decision_action": "BLIND_LABEL",
            "eligibility": final_data.get("eligibility") or final_data.get("final_eligibility"),
            "remove_reason": final_data.get("remove_reason") or "",
            "C_label": final_data.get("C_label") or final_data.get("final_c"),
            "S_label": final_data.get("S_label") or final_data.get("final_s"),
            "A_label": final_data.get("A_label") or final_data.get("final_a"),
            "uncertain": final_data.get("uncertain") in {True, "YES", "yes", "true", "TRUE"},
            "uncertainty_reason": final_data.get("uncertainty_reason") or "",
            "evidence": final_data.get("evidence") or "",
            "rule_id": final_data.get("rule_id") or "",
            "note": final_data.get("note") or "",
            "guideline_version": final_data.get("guideline_version") or "VIBSCC_Guideline_p1.0",
        })
        data = {
            "record_id": record_id,
            "adjudicator_code": admin_code,
            **final_data
        }
        clean_data = self._clean_adjudication_payload(data)
        res = self.client.table("adjudications").insert(clean_data).execute()
        self.client.table("review_routes").update({"status": "ADJUDICATED"}).eq("record_id", record_id).execute()
        return bool(res.data)

    def import_task06_bundle(self, records: List[Dict], predictions: List[Dict], routes: List[Dict]) -> Dict[str, int]:
        r_res = self.client.table("records").upsert(records, on_conflict="record_id").execute()
        p_res = self._replace_predictions_for_import(predictions)
        rt_res = self.client.table("review_routes").upsert(routes, on_conflict="record_id").execute()
        return {
            "records": len(r_res.data or []),
            "predictions": len(p_res.data or []),
            "routes": len(rt_res.data or [])
        }

    def _replace_predictions_for_import(self, predictions: List[Dict]) -> Any:
        if not predictions:
            class EmptyResponse:
                data: list[Any] = []
            return EmptyResponse()

        record_ids = sorted({row["record_id"] for row in predictions if row.get("record_id")})
        run_ids = sorted({row["run_id"] for row in predictions if row.get("run_id")})
        query = self.client.table("llm_predictions").delete()
        if record_ids:
            query = query.in_("record_id", record_ids)
        if run_ids:
            query = query.in_("run_id", run_ids)
        query.execute()
        return self.client.table("llm_predictions").insert(predictions).execute()

    def export_task07_bundle(self) -> Dict[str, Any]:
        records = self.client.table("records").select("*, review_routes(*), human_annotations(*), adjudications(*)").execute()
        return {"export_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "data": records.data}
