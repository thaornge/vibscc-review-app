import streamlit as st

from src.repository_supabase import SupabaseRepository


@st.cache_resource
def repository() -> SupabaseRepository:
    return SupabaseRepository()


def current_user(repo: SupabaseRepository):
    users = repo.client.table("users").select("*").execute().data
    users = [
        user for user in users
        if user.get("is_active", user.get("active", True)) in {True, "true", "TRUE", "1", 1}
    ]
    labels = {user["annotator_code"]: f"{user['annotator_code']} - {user['role']}" for user in users}
    annotator_code = st.sidebar.selectbox("Account", list(labels), format_func=labels.get)
    st.sidebar.caption("Supabase cloud data")
    user = next(user for user in users if user["annotator_code"] == annotator_code)
    return {**user, "user_id": annotator_code}
