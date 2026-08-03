import hmac
import os
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import dotenv_values, find_dotenv, load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
AUTH_USER_KEY = "auth_user"


def _env_values() -> dict[str, Any]:
    load_dotenv(ENV_PATH, override=False)
    values: dict[str, Any] = dict(dotenv_values(ENV_PATH))
    cwd_env = find_dotenv(usecwd=True)
    if cwd_env:
        values.update(dotenv_values(cwd_env))
    try:
        values.update(dict(st.secrets))
    except Exception:
        pass
    values.update(os.environ)
    return values


def _password_key(annotator_code: str) -> str:
    safe_code = "".join(char if char.isalnum() else "_" for char in annotator_code.upper())
    return f"APP_PASSWORD_{safe_code}"


def _account_password(annotator_code: str) -> str:
    values = _env_values()
    return str(values.get(_password_key(annotator_code), "") or "").strip()


def _active_users(repo) -> list[dict[str, Any]]:
    users = repo.client.table("users").select("*").execute().data or []
    users = [
        user for user in users
        if user.get("is_active", user.get("active", True)) in {True, "true", "TRUE", "1", 1}
    ]
    return sorted(users, key=lambda user: user["annotator_code"])


def _configured_login_count(users: list[dict[str, Any]]) -> int:
    return sum(1 for user in users if _account_password(user["annotator_code"]))


def require_login(repo) -> dict[str, Any]:
    users = _active_users(repo)
    users_by_code = {user["annotator_code"]: user for user in users}

    saved_code = st.session_state.get(AUTH_USER_KEY)
    if saved_code in users_by_code:
        user = users_by_code[saved_code]
        with st.sidebar:
            st.caption(f"Signed in as {user['annotator_code']} - {user['role']}")
            if st.button("Sign Out", use_container_width=True):
                st.session_state.pop(AUTH_USER_KEY, None)
                st.rerun()
        return {**user, "user_id": user["annotator_code"]}

    if not users:
        st.error("No active accounts are available.")
        st.stop()

    if _configured_login_count(users) == 0:
        st.error("No account passwords are configured.")
        st.info("Set APP_PASSWORD_<ANNOTATOR_CODE> in .env locally or in Streamlit secrets.")
        st.stop()

    st.title("ViBSCC Review App")
    annotator_code = st.selectbox(
        "Account",
        [user["annotator_code"] for user in users],
        format_func=lambda code: f"{code} - {users_by_code[code]['role']}",
    )
    submitted_password = st.text_input("Password", type="password")
    if not _account_password(annotator_code):
        st.caption(f"No password is configured for {annotator_code}.")
    if st.button("Sign In", type="primary"):
        expected_password = _account_password(annotator_code)
        if expected_password and hmac.compare_digest(submitted_password, expected_password):
            st.session_state[AUTH_USER_KEY] = annotator_code
            st.rerun()
        else:
            st.error("Invalid account or password.")
    st.stop()
