import streamlit as st

from src.auth import require_login
from src.app_context import repository


st.set_page_config(page_title="ViBSCC Verify", page_icon="OK", layout="wide")
st.title("ViBSCC Human Verification")

try:
    repo = repository()
except Exception as exc:
    st.error(str(exc))
    st.info("Hay dien SUPABASE_URL, SUPABASE_KEY va SUPABASE_SERVICE_ROLE_KEY trong file .env.")
    st.stop()

user = require_login(repo)

col1, col2, col3 = st.columns(3)
with col1:
    assignments = repo.get_assigned_cases_for_user(user["annotator_code"]) if user["role"] == "REVIEWER" else []
    st.metric("Assignments", len(assignments))
with col2:
    discussion = repo.get_discussion_cases(user["annotator_code"]) if user["role"] == "REVIEWER" else []
    st.metric("Discussion", len(discussion))
with col3:
    adjudication = repo.get_adjudication_cases() if user["role"] == "ADMIN" else []
    st.metric("Adjudication", len(adjudication))

st.info("Dung menu Pages de mo My Review, Discussion hoac Adjudication.")
