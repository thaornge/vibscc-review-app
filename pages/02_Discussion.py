import streamlit as st

from src.app_context import current_user, repository
from src.discussion_service import DiscussionService
from src.ui import annotation_form, labels_text


st.set_page_config(page_title="Discussion", page_icon="DS")
repo = repository()
user = current_user(repo)
service = DiscussionService(repo)

st.title("Discussion")
if user["role"] != "REVIEWER":
    st.warning("Trang nay chi danh cho REVIEWER.")
    st.stop()

cases = service.list_for_reviewer(user["user_id"])
if not cases:
    st.info("Khong co case can discussion.")
    st.stop()

item = st.selectbox(
    "Chon case",
    cases,
    format_func=lambda row: f"{row['record']['record_id']} - {row['case']['case_status']}",
)
case = item["case"]
st.info(item["record"]["text_annotation"])

st.caption("Hai initial annotations")
for label in item["labels"]:
    st.write(f"**{label['annotator_code']}** - {labels_text(label)}")

discussion = item.get("discussion")
if not discussion or discussion["discussion_status"] != "PENDING_CONFIRMATION":
    st.caption("Tao proposal")
    labels = annotation_form(f"proposal_{case['case_id']}", item["labels"][0] if item["labels"] else None)
    rationale = st.text_area("Rationale *", height=68)
    if st.button("Gui proposal", type="primary"):
        try:
            service.propose(user["user_id"], case["case_id"], labels, rationale)
            st.success("Da gui proposal.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
else:
    st.caption("Proposal dang cho")
    st.info(labels_text(discussion["proposal"]))
    st.write(discussion["rationale"])
    if discussion["proposed_by"] == user["user_id"]:
        st.warning("Dang cho reviewer con lai phan hoi.")
    else:
        rationale = st.text_area("Response rationale *", height=68)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm", type="primary", use_container_width=True):
                try:
                    service.respond(user["user_id"], case["case_id"], True, rationale)
                    st.success("Discussion da resolve.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        with col2:
            if st.button("Reject to Adjudication", use_container_width=True):
                try:
                    service.respond(user["user_id"], case["case_id"], False, rationale)
                    st.success("Da chuyen adjudication.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
