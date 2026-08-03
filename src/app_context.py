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
    users = sorted(users, key=lambda user: user["annotator_code"])
    labels = {user["annotator_code"]: f"{user['annotator_code']} - {user['role']}" for user in users}
    account_options = list(labels)

    saved_account = st.session_state.get("current_annotator_code")
    if saved_account not in account_options:
        saved_account = account_options[0]
        st.session_state["current_annotator_code"] = saved_account

    st.session_state["_account_selector"] = saved_account

    def remember_account():
        st.session_state["current_annotator_code"] = st.session_state["_account_selector"]

    annotator_code = st.sidebar.selectbox(
        "Account",
        account_options,
        format_func=labels.get,
        key="_account_selector",
        on_change=remember_account,
    )
    st.sidebar.caption("Supabase cloud data")
    user = next(user for user in users if user["annotator_code"] == annotator_code)
    return {**user, "user_id": annotator_code}
