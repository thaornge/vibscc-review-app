import streamlit as st

from src.app_context import current_user, repository
from src.ui import annotation_form, labels_text
from src.ui_supabase import first_relation, normalize_initial, to_supabase_annotation


st.set_page_config(page_title="My Review", page_icon="MR")
repo = repository()
user = current_user(repo)

st.title("My Review")
if user["role"] != "REVIEWER":
    st.warning("Trang nay chi danh cho REVIEWER.")
    st.stop()

assignments = repo.get_assigned_cases_for_user(user["annotator_code"])
editable = [row for row in assignments if row.get("status") != "SUBMITTED"]
if not editable:
    st.info("Khong co assignment chua submit.")
    st.stop()

selected = st.selectbox(
    "Chon assignment",
    editable,
    format_func=lambda row: f"{row['record_id']} - {first_relation(row, 'review_routes').get('review_route', '')} - {row.get('status', 'ASSIGNED')}",
)
record = first_relation(selected, "records")
route = first_relation(selected, "review_routes")
assignment_id = selected["assignment_id"]

st.caption(f"{selected['record_id']} - {record.get('guideline_version', '')} - {record.get('batch_id', '')}")
st.info(record.get("text_annotation", ""))

draft_rows = repo.client.table("human_annotations").select("*").eq("assignment_id", assignment_id).execute().data
defaults = normalize_initial(draft_rows[0] if draft_rows else None)

if route.get("review_route") == "SINGLE_VISIBLE_REVIEW":
    st.caption("Visible review")
    action = st.radio("Decision", ["ACCEPT", "EDIT"], horizontal=True, key=f"action_{assignment_id}")
else:
    st.caption("Blind review: predictions and other reviewer labels are hidden.")
    action = "BLIND_LABEL"

labels = annotation_form(f"review_{assignment_id}", defaults)
payload = to_supabase_annotation(labels, record_id=selected["record_id"], annotator_code=user["annotator_code"])
payload["decision_action"] = action

col1, col2 = st.columns(2)
with col1:
    if st.button("Save Draft", use_container_width=True):
        try:
            repo.save_draft(assignment_id, payload)
            st.success("Da luu draft.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
with col2:
    if st.button("Submit", type="primary", use_container_width=True):
        try:
            repo.submit_annotation(assignment_id, payload)
            st.success("Da submit.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
