from typing import Any

import streamlit as st

from .constants import A_OPTIONS, C_OPTIONS, REMOVE_REASON_OPTIONS


C1_S_OPTIONS = ["S1", "S2", "S3", "S4", "S5", "S6"]


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


def annotation_form(prefix: str, initial: dict[str, Any] | None = None, *, disabled: bool = False) -> dict[str, Any]:
    compact_form_styles()
    initial = initial or {}
    eligibility = st.radio("Eligibility", ["KEEP", "REMOVE"], index=0 if initial.get("eligibility", "KEEP") == "KEEP" else 1, horizontal=True, key=f"{prefix}_eligibility", disabled=disabled)
    if eligibility == "REMOVE":
        remove_value = initial.get("remove_reason") if initial.get("remove_reason") in REMOVE_REASON_OPTIONS else REMOVE_REASON_OPTIONS[0]
        remove_reason = st.radio("Remove reason *", REMOVE_REASON_OPTIONS, index=REMOVE_REASON_OPTIONS.index(remove_value), horizontal=True, key=f"{prefix}_remove", disabled=disabled)
        c_label = s_label = a_label = None
    else:
        c_col, s_col, a_col = st.columns([1.1, 2, 2.2])
        c_options = C_OPTIONS
        with c_col:
            c_label = st.radio("C label", c_options, index=c_options.index(initial.get("C_label", "C0")), horizontal=True, key=f"{prefix}_c", disabled=disabled)
        s_options = ["S0"] if c_label in {"C0", "C2"} else C1_S_OPTIONS
        a_options = ["A0"] if c_label == "C0" else A_OPTIONS[1:]
        s_value = initial.get("S_label") if initial.get("S_label") in s_options else s_options[0]
        a_value = initial.get("A_label") if initial.get("A_label") in a_options else a_options[0]
        with s_col:
            s_label = st.radio("S label", s_options, index=s_options.index(s_value), horizontal=True, key=f"{prefix}_s", disabled=disabled)
        with a_col:
            a_label = st.radio("A label", a_options, index=a_options.index(a_value), horizontal=True, key=f"{prefix}_a", disabled=disabled)
        remove_reason = None
    uncertain_col, reason_col, rule_col = st.columns([0.8, 2.2, 1])
    with uncertain_col:
        uncertain = st.checkbox("Uncertain", value=bool(initial.get("uncertain", False)), key=f"{prefix}_uncertain", disabled=disabled)
    with reason_col:
        uncertainty_reason = st.text_input("Uncertainty reason *" if uncertain else "Uncertainty reason", value=initial.get("uncertainty_reason") or "", disabled=disabled or not uncertain, key=f"{prefix}_uncertainty_reason")
    with rule_col:
        rule_id = st.text_input("Rule ID", value=initial.get("rule_id") or "", key=f"{prefix}_rule", disabled=disabled)
    note_label = "Note *" if eligibility == "REMOVE" and remove_reason == "OTHER_REMOVE" else "Note"
    evidence_col, note_col = st.columns(2)
    with evidence_col:
        evidence = st.text_area("Evidence", value=initial.get("evidence") or "", height=68, key=f"{prefix}_evidence", disabled=disabled)
    with note_col:
        note = st.text_area(note_label, value=initial.get("note") or "", height=68, key=f"{prefix}_note", disabled=disabled)
    return {"eligibility": eligibility, "remove_reason": remove_reason, "C_label": c_label, "S_label": s_label, "A_label": a_label, "uncertain": uncertain, "uncertainty_reason": (uncertainty_reason or None) if uncertain else None, "evidence": evidence, "rule_id": rule_id, "note": note, "guideline_version": "VIBSCC_Guideline_p1.0"}


def labels_text(labels: dict[str, Any] | None) -> str:
    if not labels: return "—"
    if labels.get("eligibility") == "REMOVE": return f"REMOVE · {labels.get('remove_reason', '')}"
    return " · ".join(str(labels.get(k, "")) for k in ("eligibility", "C_label", "S_label", "A_label"))
