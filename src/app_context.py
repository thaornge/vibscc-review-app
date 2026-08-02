from pathlib import Path

import streamlit as st

from src.mock_seed import build_mock_store
from src.repository_fake import FakeRepository


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / ".local" / "mock_state.json"


@st.cache_resource
def repository() -> FakeRepository:
    return FakeRepository(DB_PATH, build_mock_store)


def current_user(repo: FakeRepository):
    users = repo.snapshot()["users"]
    labels = {
        user_id: f"{user['annotator_code']} - {user['role']}"
        for user_id, user in users.items()
        if user["is_active"]
    }
    user_id = st.sidebar.selectbox("Mock account", list(labels), format_func=labels.get)
    st.sidebar.caption("Checkpoint mock login - not for production")
    return {**users[user_id], "user_id": user_id}
