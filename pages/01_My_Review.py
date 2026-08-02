import streamlit as st

from src.app_context import current_user, repository
from src.review_service import ReviewService
from src.ui import annotation_form, labels_text


FINAL_STATUSES = {
    "RESOLVED_HUMAN_AGREEMENT",
    "RESOLVED_DISCUSSION",
    "RESOLVED_ADJUDICATION",
    "RESOLVED_VISIBLE_ACCEPT",
    "RESOLVED_VISIBLE_EDIT",
}


st.set_page_config(page_title="My Review", page_icon="MR")
repo = repository()
user = current_user(repo)
service = ReviewService(repo)

st.title("My Review")
if user["role"] != "REVIEWER":
    st.warning("Trang nay chi danh cho REVIEWER.")
    st.stop()

assignments = service.list_assignments(user["user_id"])
editable = [row for row in assignments if row["assignment_status"] != "SUBMITTED"]
if not editable:
    st.info("Khong co assignment chua submit.")
    st.stop()

selected = st.selectbox(
    "Chon assignment",
    editable,
    format_func=lambda row: f"{row['record_id']} - {row['visibility_mode']} - {row['assignment_status']}",
)
view = service.reviewer_view(user["user_id"], selected["assignment_id"])
assignment = view["assignment"]

st.caption(f"{view['record']['record_id']} - {view['record']['guideline_version']} - {view['record']['batch_id']}")
st.info(view["record"]["text_annotation"])

defaults = view.get("draft") or {}
if view["visibility_mode"] == "VISIBLE":
    consensus = view["llm_consensus"]
    st.caption(f"LLM consensus: {labels_text(consensus)}")
    if consensus.get("evidence"):
        st.caption(consensus["evidence"])
    action = st.radio("Decision", ["ACCEPT", "EDIT"], horizontal=True, key=f"action_{assignment['assignment_id']}")
    if action == "ACCEPT":
        defaults = {**defaults, **consensus}
else:
    action = "BLIND_LABEL"
    st.caption("Blind review: predictions and other reviewer labels are hidden.")

if view["case_status"] in FINAL_STATUSES or assignment["assignment_status"] == "SUBMITTED":
    st.success("Initial annotation da submit va bi khoa.")
    st.stop()

labels = annotation_form(f"review_{assignment['assignment_id']}", defaults)
labels["decision_action"] = action

col1, col2 = st.columns(2)
with col1:
    if st.button("Save Draft", use_container_width=True):
        try:
            service.save_draft(user["user_id"], assignment["assignment_id"], labels, assignment["row_version"])
            st.success("Da luu draft.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
with col2:
    if st.button("Submit", type="primary", use_container_width=True):
        try:
            status = service.submit(user["user_id"], assignment["assignment_id"], labels, assignment["row_version"])
            st.success(f"Da submit. Case status: {status}")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
