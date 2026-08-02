import streamlit as st

from src.app_context import current_user, repository
from src.ui import annotation_form, labels_text
from src.ui_supabase import first_relation, normalize_initial, to_supabase_annotation


st.set_page_config(page_title="Discussion", page_icon="DS")
repo = repository()
user = current_user(repo)

st.title("Discussion")
if user["role"] != "REVIEWER":
    st.warning("Trang nay chi danh cho REVIEWER.")
    st.stop()

cases = repo.get_discussion_cases(user["annotator_code"])
if not cases:
    st.info("Khong co case can discussion.")
    st.stop()

item = st.selectbox(
    "Chon case",
    cases,
    format_func=lambda row: f"{row['record_id']} - {row.get('status', '')}",
)
record = first_relation(item, "records")
annotations = item.get("human_annotations") or []
discussions = item.get("discussions") or []
open_discussion = next((disc for disc in discussions if disc.get("status") == "OPEN"), None)

st.info(record.get("text_annotation", ""))
st.caption("Hai initial annotations")
for annotation in annotations:
    st.write(f"**{annotation.get('annotator_code', '')}** - {labels_text(normalize_initial(annotation))}")

if not open_discussion:
    st.caption("Tao proposal")
    labels = annotation_form(f"proposal_{item['record_id']}", normalize_initial(annotations[0] if annotations else None))
    rationale = st.text_area("Rationale *", height=68)
    payload = to_supabase_annotation(labels, record_id=item["record_id"], annotator_code=user["annotator_code"])
    payload["rationale"] = rationale
    if st.button("Gui proposal", type="primary"):
        try:
            repo.submit_proposal(item["record_id"], user["annotator_code"], payload)
            st.success("Da gui proposal.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
else:
    st.caption("Proposal dang cho")
    st.info(labels_text(normalize_initial(open_discussion)))
    st.write(open_discussion.get("rationale") or "")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm", type="primary", use_container_width=True):
            try:
                repo.resolve_discussion(open_discussion["discussion_id"], user["annotator_code"], "ACCEPT")
                st.success("Discussion da resolve.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    with col2:
        if st.button("Reject to Adjudication", use_container_width=True):
            try:
                repo.resolve_discussion(open_discussion["discussion_id"], user["annotator_code"], "REJECT")
                st.success("Da chuyen adjudication.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
