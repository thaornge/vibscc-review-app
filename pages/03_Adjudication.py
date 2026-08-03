import streamlit as st

from src.auth import require_login
from src.app_context import repository
from src.ui import annotation_form, labels_text
from src.ui_supabase import first_relation, normalize_initial, to_supabase_annotation
from src.validators import validate_annotation


st.set_page_config(page_title="Adjudication", page_icon="AD", layout="wide")
repo = repository()
user = require_login(repo)

st.title("Adjudication")
if user["role"] != "ADMIN":
    st.error("Chi ADMIN duoc truy cap.")
    st.stop()

cases = repo.get_adjudication_cases()
if not cases:
    st.info("Khong co case cho adjudication.")
    st.stop()

item = st.selectbox(
    "Chon case",
    cases,
    format_func=lambda row: f"{row['record_id']} - {row.get('status', '')}",
)
record = first_relation(item, "records")
annotations = item.get("human_annotations") or []
discussions = item.get("discussions") or []
latest_discussion = discussions[-1] if discussions else {}

st.info(record.get("text_annotation", ""))
for annotation in annotations:
    st.write(f"**{annotation.get('annotator_code', '')}** - {labels_text(normalize_initial(annotation))}")
if latest_discussion:
    st.caption(latest_discussion.get("rationale") or latest_discussion.get("reason") or "")

labels = annotation_form(f"adjudication_{item['record_id']}", normalize_initial(latest_discussion or (annotations[0] if annotations else None)))
rationale = st.text_area("Rationale *", height=68)
payload = to_supabase_annotation(labels, record_id=item["record_id"], annotator_code=user["annotator_code"])
payload.update({
    "final_eligibility": labels.get("eligibility"),
    "final_c": labels.get("C_label") if labels.get("eligibility") != "REMOVE" else None,
    "final_s": labels.get("S_label") if labels.get("eligibility") != "REMOVE" else None,
    "final_a": labels.get("A_label") if labels.get("eligibility") != "REMOVE" else None,
    "rationale": rationale,
    "reasoning": rationale,
})
if st.button("Submit Adjudication", type="primary"):
    try:
        validate_annotation({**labels, "decision_action": "BLIND_LABEL"})
        if not rationale.strip():
            raise ValueError("Rationale is required")
        repo.submit_adjudication(item["record_id"], user["annotator_code"], payload)
        st.success("Da adjudicate va resolve case.")
        st.rerun()
    except Exception as exc:
        st.error(str(exc))
