import streamlit as st

from src.app_context import current_user, repository
from src.ui import annotation_form, labels_text
from src.ui_supabase import first_relation, normalize_initial, to_supabase_annotation


st.set_page_config(page_title="Adjudication", page_icon="AD")
repo = repository()
user = current_user(repo)

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
    st.caption(latest_discussion.get("rationale") or "")

labels = annotation_form(f"adjudication_{item['record_id']}", normalize_initial(latest_discussion or (annotations[0] if annotations else None)))
rationale = st.text_area("Rationale *", height=68)
payload = to_supabase_annotation(labels, record_id=item["record_id"], annotator_code=user["annotator_code"])
payload["rationale"] = rationale
if st.button("Submit Adjudication", type="primary"):
    try:
        repo.submit_adjudication(item["record_id"], user["annotator_code"], payload)
        st.success("Da adjudicate va resolve case.")
        st.rerun()
    except Exception as exc:
        st.error(str(exc))
