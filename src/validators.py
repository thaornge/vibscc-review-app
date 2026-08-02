from typing import Any


class ValidationError(ValueError):
    pass


def label_tuple(annotation: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    return tuple(annotation.get(k) for k in ("eligibility", "C_label", "S_label", "A_label"))


def validate_annotation(data: dict[str, Any]) -> None:
    eligibility = data.get("eligibility")
    c_label, s_label, a_label = (data.get("C_label"), data.get("S_label"), data.get("A_label"))
    if eligibility not in {"KEEP", "REMOVE"}:
        raise ValidationError("Eligibility phải là KEEP hoặc REMOVE.")
    if eligibility == "REMOVE":
        if any((c_label, s_label, a_label)):
            raise ValidationError("REMOVE yêu cầu C/S/A để trống.")
        if not str(data.get("remove_reason") or "").strip():
            raise ValidationError("REMOVE bắt buộc có remove_reason.")
    else:
        if c_label == "C0" and (s_label, a_label) != ("S0", "A0"):
            raise ValidationError("C0 chỉ hợp lệ với S0 và A0.")
        if c_label == "C1" and (s_label not in {f"S{i}" for i in range(1, 7)} or a_label not in {f"A{i}" for i in range(1, 8)}):
            raise ValidationError("C1 yêu cầu S1-S6 và A1-A7.")
        if c_label == "C2" and (s_label != "S0" or a_label not in {f"A{i}" for i in range(1, 8)}):
            raise ValidationError("C2 yêu cầu S0 và A1-A7.")
        if c_label not in {"C0", "C1", "C2"}:
            raise ValidationError("Nhãn C không hợp lệ.")
    if bool(data.get("uncertain")) and not str(data.get("uncertainty_reason") or "").strip():
        raise ValidationError("Uncertain bắt buộc có uncertainty_reason.")


def normalized_annotation(data: dict[str, Any]) -> dict[str, Any]:
    result = dict(data)
    if result.get("eligibility") == "REMOVE":
        result.update({"C_label": None, "S_label": None, "A_label": None})
    result["uncertain"] = bool(result.get("uncertain", False))
    validate_annotation(result)
    return result
