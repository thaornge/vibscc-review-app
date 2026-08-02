import streamlit as st
from src.app_context import current_user, repository

st.set_page_config(page_title="ViBSCC Review", page_icon="✅", layout="centered")
repo = repository()
user = current_user(repo)

st.title("ViBSCC Human Verification")
st.write("Ứng dụng mock cho quy trình blind review, visible review, discussion và adjudication.")

left, right = st.columns(2)
with left:
    st.metric("Assignments của tôi", len(repo.assignments_for(user["user_id"])) if user["role"] == "REVIEWER" else 0)
with right:
    st.metric("Chờ adjudication", len(repo.adjudication_cases()) if user["role"] == "ADMIN" else 0)

st.info("Dùng menu Pages để mở My Review, Discussion hoặc Adjudication.")
if st.button("Reset toàn bộ mock data"):
    repo.reset()
    st.success("Đã reset mock data.")
    st.rerun()
