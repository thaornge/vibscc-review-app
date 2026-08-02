import streamlit as st
from src.app_context import current_user, repository
from src.ui import annotation_form, labels_text

st.set_page_config(page_title="Adjudication", page_icon="⚖️")
repo = repository(); user = current_user(repo)
st.title("Adjudication")
if user["role"] != "ADMIN": st.error("Chỉ ADMIN được truy cập."); st.stop()
cases = repo.adjudication_cases()
if not cases: st.info("Không có case chờ adjudication."); st.stop()
case = st.selectbox("Chọn case", cases, format_func=lambda x: f"{x['record_id']} · {x['case_id']}")
st.write(case["text_annotation"])
for item in case["assignments"]:
    st.write(f"**{item['reviewer_id']}** — {labels_text(item.get('annotation'))}")
labels = annotation_form(f"adjudication_{case['case_id']}")
rationale = st.text_area("Rationale *")
if st.button("Submit Adjudication", type="primary"):
    try: repo.adjudicate(case["case_id"], user["user_id"], labels, rationale); st.success("Đã adjudicate và resolve case."); st.rerun()
    except ValueError as exc: st.error(str(exc))
