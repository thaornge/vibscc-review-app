import streamlit as st
from src.app_context import current_user, repository
from src.constants import CaseStatus
from src.ui import annotation_form, labels_text

st.set_page_config(page_title="Discussion", page_icon="💬")
repo = repository(); user = current_user(repo)
st.title("Discussion")
if user["role"] != "REVIEWER": st.warning("Trang này chỉ dành cho REVIEWER."); st.stop()
cases = repo.discussion_cases_for(user["user_id"])
if not cases: st.info("Không có case cần discussion."); st.stop()
case = st.selectbox("Chọn case", cases, format_func=lambda x: f"{x['record_id']} · {x['status']}")
st.write(case["text_annotation"])
st.subheader("Hai initial annotations")
for item in case.get("submitted_annotations", []): st.write(f"**{item['reviewer_id']}** — {labels_text(item)}")

if case["status"] == CaseStatus.DISCUSSION_REQUIRED:
    st.subheader("Tạo proposal")
    labels = annotation_form(f"proposal_{case['case_id']}")
    rationale = st.text_area("Rationale *")
    if st.button("Gửi proposal", type="primary"):
        try: repo.propose(case["case_id"], user["user_id"], labels, rationale); st.success("Đã gửi proposal."); st.rerun()
        except ValueError as exc: st.error(str(exc))
else:
    proposal = case["discussion"]
    st.subheader("Proposal đang chờ")
    st.info(labels_text(proposal["labels"]))
    st.write(proposal["rationale"])
    if proposal["proposed_by"] == user["user_id"]:
        st.warning("Đang chờ reviewer còn lại phản hồi.")
    else:
        rationale = st.text_area("Response rationale *")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Confirm", type="primary", use_container_width=True):
                try: repo.respond(case["case_id"], user["user_id"], True, rationale); st.success("Discussion đã resolve."); st.rerun()
                except ValueError as exc: st.error(str(exc))
        with c2:
            if st.button("Reject → Adjudication", use_container_width=True):
                try: repo.respond(case["case_id"], user["user_id"], False, rationale); st.success("Đã chuyển adjudication."); st.rerun()
                except ValueError as exc: st.error(str(exc))
