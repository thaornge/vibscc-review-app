from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import streamlit as st

from src.adjudication_service import AdjudicationService
from src.constants import A_OPTIONS, C_OPTIONS, REMOVE_REASON_OPTIONS
from src.discussion_service import DiscussionService
from src.mock_seed import build_mock_store
from src.repository_fake import FakeRepository
from src.review_service import ReviewService


ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("VIBSCC_MOCK_DB_PATH", ROOT / ".local" / "mock_state.json"))
C1_S_OPTIONS = ["S1", "S2", "S3", "S4", "S5", "S6"]


@st.cache_resource
def repository() -> FakeRepository:
    return FakeRepository(DB_PATH, build_mock_store)


def compact_form_styles() -> None:
    st.markdown(
        """
        <style>
        div[data-testid="stRadio"] { margin-bottom: -0.45rem; }
        div[data-testid="stRadio"] > label,
        div[data-testid="stCheckbox"] > label,
        div[data-testid="stTextInput"] > label,
        div[data-testid="stTextArea"] > label { padding-bottom: 0.1rem; }
        div[data-testid="stVerticalBlock"] { gap: 0.35rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def label_form(prefix: str, defaults: dict[str, Any], *, disabled: bool = False) -> dict[str, Any]:
    compact_form_styles()
    eligibility = st.radio("Eligibility", ["KEEP", "REMOVE"], index=0 if defaults.get("eligibility", "KEEP") == "KEEP" else 1, horizontal=True, key=f"{prefix}_eligibility", disabled=disabled)
    if eligibility == "REMOVE":
        remove_value = defaults.get("remove_reason") if defaults.get("remove_reason") in REMOVE_REASON_OPTIONS else REMOVE_REASON_OPTIONS[0]
        remove_reason = st.radio("Remove reason *", REMOVE_REASON_OPTIONS, index=REMOVE_REASON_OPTIONS.index(remove_value), horizontal=True, key=f"{prefix}_remove", disabled=disabled)
        c_label = s_label = a_label = ""
    else:
        c_col, s_col, a_col = st.columns([1.1, 2, 2.2])
        remove_reason = ""
        c_options = C_OPTIONS
        with c_col:
            c_label = st.radio("C", c_options, index=c_options.index(defaults.get("C_label", "C0")), horizontal=True, key=f"{prefix}_c", disabled=disabled)
        s_options = ["S0"] if c_label in {"C0", "C2"} else C1_S_OPTIONS
        a_options = ["A0"] if c_label == "C0" else A_OPTIONS[1:]
        default_s = defaults.get("S_label") if defaults.get("S_label") in s_options else s_options[0]
        default_a = defaults.get("A_label") if defaults.get("A_label") in a_options else a_options[0]
        with s_col:
            s_label = st.radio("S", s_options, index=s_options.index(default_s), horizontal=True, key=f"{prefix}_s", disabled=disabled)
        with a_col:
            a_label = st.radio("A", a_options, index=a_options.index(default_a), horizontal=True, key=f"{prefix}_a", disabled=disabled)
    uncertain_col, reason_col, rule_col = st.columns([0.8, 2.2, 1])
    with uncertain_col:
        uncertain = st.checkbox("Uncertain", value=bool(defaults.get("uncertain", False)), key=f"{prefix}_uncertain", disabled=disabled)
    with reason_col:
        uncertainty_reason = st.text_input("Uncertainty reason *" if uncertain else "Uncertainty reason", value=defaults.get("uncertainty_reason", ""), key=f"{prefix}_uncertainty_reason", disabled=disabled or not uncertain)
    with rule_col:
        rule_id = st.text_input("Rule ID", value=defaults.get("rule_id", ""), key=f"{prefix}_rule", disabled=disabled)
    note_label = "Note / edit reason *" if eligibility == "REMOVE" and remove_reason == "OTHER_REMOVE" else "Note / edit reason"
    evidence_col, note_col = st.columns(2)
    with evidence_col:
        evidence = st.text_area("Evidence", value=defaults.get("evidence", ""), height=68, key=f"{prefix}_evidence", disabled=disabled)
    with note_col:
        note = st.text_area(note_label, value=defaults.get("note", ""), height=68, key=f"{prefix}_note", disabled=disabled)
    return {"eligibility": eligibility, "remove_reason": remove_reason, "C_label": c_label, "S_label": s_label, "A_label": a_label, "uncertain": uncertain, "uncertainty_reason": uncertainty_reason if uncertain else "", "evidence": evidence, "rule_id": rule_id, "note": note, "guideline_version": "p1.0-mock"}


def my_review(user_id: str) -> None:
    service = ReviewService(repository())
    assignments = service.list_assignments(user_id)
    editable = [row for row in assignments if row["assignment_status"] != "SUBMITTED"]
    st.subheader("My review")
    if not editable:
        st.info("Không còn assignment chưa submit cho tài khoản này.")
        return
    labels = {f"{row['assignment_id']} · {row['record_id']} · {row['visibility_mode']}": row["assignment_id"] for row in editable}
    selected = st.selectbox("Assignment", list(labels))
    view = service.reviewer_view(user_id, labels[selected])
    assignment = view["assignment"]
    st.caption(f"{view['record']['record_id']} · batch {view['record']['batch_id']} · guideline {view['record']['guideline_version']}")
    st.info(view["record"]["text_annotation"])
    defaults = view.get("draft") or {}
    if view["visibility_mode"] == "VISIBLE":
        consensus = view["llm_consensus"]
        st.info(f"LLM consensus: {consensus['eligibility']} / {consensus['C_label']} / {consensus['S_label']} / {consensus['A_label']}")
        action = st.radio("Action", ["ACCEPT", "EDIT"], horizontal=True, key=f"action_{assignment['assignment_id']}")
        if action == "ACCEPT":
            defaults = {**defaults, **consensus}
        annotation = label_form(assignment["assignment_id"], defaults, disabled=action == "ACCEPT")
    else:
        action = "BLIND_LABEL"
        st.warning("Blind mode: LLM predictions, audit flag và nhãn reviewer khác được ẩn.")
        annotation = label_form(assignment["assignment_id"], defaults)
    annotation["decision_action"] = action
    col1, col2 = st.columns(2)
    if col1.button("Save draft", use_container_width=True):
        try:
            service.save_draft(user_id, assignment["assignment_id"], annotation, assignment["row_version"])
            st.success("Draft đã lưu bền vững.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
    if col2.button("Submit & lock", type="primary", use_container_width=True):
        try:
            status = service.submit(user_id, assignment["assignment_id"], annotation, assignment["row_version"])
            st.success(f"Đã submit. Case status: {status}")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))


def discussion(user_id: str) -> None:
    service = DiscussionService(repository())
    cases = service.list_for_reviewer(user_id)
    st.subheader("Discussion")
    if not cases:
        st.info("Không có case discussion cho tài khoản này.")
        return
    selected = st.selectbox("Case", range(len(cases)), format_func=lambda i: cases[i]["case"]["case_id"])
    item = cases[selected]
    st.write(item["record"]["text_annotation"])
    st.dataframe([{key: value for key, value in label.items() if key in {"review_slot", "annotator_code", "eligibility", "C_label", "S_label", "A_label", "evidence", "note"}} for label in item["labels"]], use_container_width=True)
    existing = item.get("discussion")
    if existing and existing["discussion_status"] == "PENDING_CONFIRMATION":
        st.write("Proposal", existing["proposal"])
        if existing["proposed_by"] == user_id:
            st.info("Đang chờ reviewer còn lại xác nhận.")
            return
        reject_reason = st.text_input("Reject/escalate reason")
        c1, c2 = st.columns(2)
        if c1.button("Confirm proposal"):
            service.respond(user_id, item["case"]["case_id"], True)
            st.rerun()
        if c2.button("Reject → adjudication"):
            try:
                service.respond(user_id, item["case"]["case_id"], False, reject_reason)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    else:
        proposal = label_form(f"discussion_{item['case']['case_id']}", item["labels"][0])
        rationale = st.text_area("Proposal rationale")
        if st.button("Submit proposal", type="primary"):
            try:
                service.propose(user_id, item["case"]["case_id"], proposal, rationale)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))


def adjudication(user_id: str) -> None:
    service = AdjudicationService(repository())
    st.subheader("Adjudication")
    try:
        cases = service.list_pending(user_id)
    except Exception as exc:
        st.error(str(exc))
        return
    if not cases:
        st.info("Không có case chờ adjudication.")
        return
    selected = st.selectbox("Pending case", range(len(cases)), format_func=lambda i: cases[i]["case"]["case_id"])
    item = cases[selected]
    st.write(item["record"]["text_annotation"])
    if item["discussion"]:
        st.caption(item["discussion"]["rationale"])
    annotation = label_form(f"adj_{item['case']['case_id']}", item.get("discussion", {}).get("proposal", {}))
    rationale = st.text_area("Adjudication rationale")
    if st.button("Resolve adjudication", type="primary"):
        try:
            service.resolve(user_id, item["case"]["case_id"], annotation, rationale)
            st.rerun()
        except Exception as exc:
            st.error(str(exc))


st.set_page_config(page_title="ViBSCC Verify", page_icon="✅", layout="wide")
st.title("ViBSCC Human Verification · Mock Checkpoint 2")
data = repository().snapshot()
active_users = [value for value in data["users"].values() if value["is_active"]]
user_id = st.sidebar.selectbox("Mock login", [user["annotator_code"] for user in active_users])
role = data["users"][user_id]["role"]
screen_options = ["My Review", "Discussion"] + (["Adjudication", "Admin"] if role == "ADMIN" else [])
screen = st.sidebar.radio("Screen", screen_options)
st.sidebar.caption(f"Role: {role} · persistent mock: {DB_PATH.name}")

if screen == "My Review":
    my_review(user_id)
elif screen == "Discussion":
    discussion(user_id)
elif screen == "Adjudication":
    adjudication(user_id)
else:
    st.subheader("Admin mock controls")
    counts = {"records": len(data["records"]), "cases": len(data["cases"]), "assignments": len(data["assignments"]), "submitted": sum(a["assignment_status"] == "SUBMITTED" for a in data["assignments"].values())}
    st.json(counts)
    if st.button("Reset synthetic mock data"):
        repository().reset()
        st.rerun()
