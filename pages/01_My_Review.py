import streamlit as st
from src.app_context import current_user, repository
from src.constants import FINAL_STATUSES, Route
from src.ui import annotation_form, labels_text

st.set_page_config(page_title="My Review", page_icon="📝")
repo = repository(); user = current_user(repo)
st.title("My Review")
if user["role"] != "REVIEWER":
    st.warning("Trang này chỉ dành cho REVIEWER."); st.stop()

assignments = repo.assignments_for(user["user_id"])
if not assignments:
    st.info("Không có assignment."); st.stop()
selected = st.selectbox("Chọn assignment", assignments, format_func=lambda x: f"{x['record_id']} · {x['route']} · {x['status']}")
case = repo.case_for_reviewer(selected["case_id"], user["user_id"])
st.caption(f"{case['record_id']} · {case['guideline_version']} · {case['batch_id']}")
st.subheader("Nội dung")
st.write(case["text_annotation"])

if case["route"] == Route.SINGLE_VISIBLE_REVIEW:
    st.subheader("LLM consensus")
    st.info(labels_text(case["llm_consensus"]))
    if case["llm_consensus"].get("evidence"): st.caption(case["llm_consensus"]["evidence"])
else:
    st.info("Blind review: hãy tự gán nhãn. Prediction và reviewer khác được bảo vệ cho tới discussion.")

if selected["status"] in FINAL_STATUSES or case["assignment"]["status"] == "SUBMITTED":
    st.success("Initial annotation đã submit và bị khóa."); st.stop()

initial = case["assignment"].get("draft") or (case.get("llm_consensus") if case["route"] == Route.SINGLE_VISIBLE_REVIEW else None)
labels = annotation_form(f"review_{case['case_id']}", initial)
if case["route"] == Route.SINGLE_VISIBLE_REVIEW:
    action = st.radio("Decision", ["ACCEPT", "EDIT"], horizontal=True)
    if action == "ACCEPT": labels = {**case["llm_consensus"], "guideline_version": case["guideline_version"]}
else:
    action = "BLIND_LABEL"

c1, c2 = st.columns(2)
with c1:
    if st.button("Save Draft", use_container_width=True):
        try: repo.save_draft(case["case_id"], user["user_id"], labels); st.success("Đã lưu draft.")
        except ValueError as exc: st.error(str(exc))
with c2:
    if st.button("Submit", type="primary", use_container_width=True):
        try: repo.submit(case["case_id"], user["user_id"], labels, action); st.success("Đã submit và khóa initial annotation."); st.rerun()
        except ValueError as exc: st.error(str(exc))
