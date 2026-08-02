import streamlit as st

from src.adjudication_service import AdjudicationService
from src.app_context import current_user, repository
from src.ui import annotation_form, labels_text


st.set_page_config(page_title="Adjudication", page_icon="AD")
repo = repository()
user = current_user(repo)
service = AdjudicationService(repo)

st.title("Adjudication")
if user["role"] != "ADMIN":
    st.error("Chi ADMIN duoc truy cap.")
    st.stop()

try:
    cases = service.list_pending(user["user_id"])
except Exception as exc:
    st.error(str(exc))
    st.stop()

if not cases:
    st.info("Khong co case cho adjudication.")
    st.stop()

item = st.selectbox(
    "Chon case",
    cases,
    format_func=lambda row: f"{row['record']['record_id']} - {row['case']['case_id']}",
)
case = item["case"]
st.info(item["record"]["text_annotation"])
if item.get("discussion"):
    st.caption(item["discussion"]["rationale"])
    st.write(labels_text(item["discussion"].get("proposal")))

labels = annotation_form(f"adjudication_{case['case_id']}", item.get("discussion", {}).get("proposal", {}))
rationale = st.text_area("Rationale *", height=68)
if st.button("Submit Adjudication", type="primary"):
    try:
        service.resolve(user["user_id"], case["case_id"], labels, rationale)
        st.success("Da adjudicate va resolve case.")
        st.rerun()
    except Exception as exc:
        st.error(str(exc))
