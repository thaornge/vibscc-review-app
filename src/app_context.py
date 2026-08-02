import streamlit as st
from src.repository_fake import FakeRepository


def repository() -> FakeRepository:
    return FakeRepository()


def current_user(repo: FakeRepository):
    users = repo.users()
    labels = {u["user_id"]: f"{u['annotator_code']} · {u['role']}" for u in users}
    user_id = st.sidebar.selectbox("Mock account", list(labels), format_func=labels.get)
    user = next(u for u in users if u["user_id"] == user_id)
    st.sidebar.caption("Checkpoint mock login — không dùng cho production")
    return user
