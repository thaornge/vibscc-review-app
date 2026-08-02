from typing import Any
import streamlit as st


def annotation_form(prefix: str, initial: dict[str, Any] | None = None) -> dict[str, Any]:
    initial = initial or {}
    eligibility = st.radio("Eligibility", ["KEEP", "REMOVE"], index=0 if initial.get("eligibility", "KEEP") == "KEEP" else 1, horizontal=True, key=f"{prefix}_eligibility")
    if eligibility == "REMOVE":
        remove_reason = st.text_input("Remove reason *", value=initial.get("remove_reason") or "", key=f"{prefix}_remove")
        c_label = s_label = a_label = None
    else:
        c_options = ["C0", "C1", "C2"]
        c_label = st.selectbox("C label", c_options, index=c_options.index(initial.get("C_label", "C0")), key=f"{prefix}_c")
        s_options = ["S0"] if c_label in {"C0", "C2"} else [f"S{i}" for i in range(1, 7)]
        a_options = ["A0"] if c_label == "C0" else [f"A{i}" for i in range(1, 8)]
        s_value = initial.get("S_label") if initial.get("S_label") in s_options else s_options[0]
        a_value = initial.get("A_label") if initial.get("A_label") in a_options else a_options[0]
        s_label = st.selectbox("S label", s_options, index=s_options.index(s_value), key=f"{prefix}_s")
        a_label = st.selectbox("A label", a_options, index=a_options.index(a_value), key=f"{prefix}_a")
        remove_reason = None
    uncertain = st.checkbox("Uncertain", value=bool(initial.get("uncertain", False)), key=f"{prefix}_uncertain")
    uncertainty_reason = st.text_input("Uncertainty reason *" if uncertain else "Uncertainty reason", value=initial.get("uncertainty_reason") or "", disabled=not uncertain, key=f"{prefix}_uncertainty_reason")
    evidence = st.text_area("Evidence", value=initial.get("evidence") or "", key=f"{prefix}_evidence")
    rule_id = st.text_input("Rule ID", value=initial.get("rule_id") or "", key=f"{prefix}_rule")
    note = st.text_area("Note", value=initial.get("note") or "", key=f"{prefix}_note")
    return {"eligibility": eligibility, "remove_reason": remove_reason, "C_label": c_label, "S_label": s_label, "A_label": a_label, "uncertain": uncertain, "uncertainty_reason": uncertainty_reason or None, "evidence": evidence, "rule_id": rule_id, "note": note, "guideline_version": "VIBSCC_Guideline_p1.0"}


def labels_text(labels: dict[str, Any] | None) -> str:
    if not labels: return "—"
    if labels.get("eligibility") == "REMOVE": return f"REMOVE · {labels.get('remove_reason', '')}"
    return " · ".join(str(labels.get(k, "")) for k in ("eligibility", "C_label", "S_label", "A_label"))
