from src.constants import CaseStatus


class InvalidTransition(ValueError):
    pass


ALLOWED = {
    CaseStatus.ASSIGNED: {CaseStatus.IN_REVIEW, CaseStatus.WAITING_SECOND_REVIEW, CaseStatus.RESOLVED_VISIBLE_ACCEPT, CaseStatus.RESOLVED_VISIBLE_EDIT},
    CaseStatus.IN_REVIEW: {CaseStatus.WAITING_SECOND_REVIEW, CaseStatus.RESOLVED_VISIBLE_ACCEPT, CaseStatus.RESOLVED_VISIBLE_EDIT},
    CaseStatus.WAITING_SECOND_REVIEW: {CaseStatus.RESOLVED_HUMAN_AGREEMENT, CaseStatus.DISCUSSION_REQUIRED},
    CaseStatus.DISCUSSION_REQUIRED: {CaseStatus.DISCUSSION_IN_PROGRESS, CaseStatus.ADJUDICATION_REQUIRED},
    CaseStatus.DISCUSSION_IN_PROGRESS: {CaseStatus.RESOLVED_DISCUSSION, CaseStatus.ADJUDICATION_REQUIRED},
    CaseStatus.ADJUDICATION_REQUIRED: {CaseStatus.RESOLVED_ADJUDICATION},
}


def assert_transition(current: str, target: str) -> None:
    current_status, target_status = CaseStatus(current), CaseStatus(target)
    if target_status not in ALLOWED.get(current_status, set()):
        raise InvalidTransition(f"Không thể chuyển {current_status} → {target_status}")
