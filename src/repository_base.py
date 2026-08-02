# src/repository_base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable, Protocol, TypeVar, List, Dict, Optional

T = TypeVar("T")

# Interface tầng State/Persistence
class Repository(Protocol):
    """Interface Nga and Ngoc agree on for UI/persistence integration.

    A real adapter must provide snapshot reads and serializable atomic updates.
    The callback receives the complete normalized store and must either finish
    successfully or raise, in which case no state is committed.
    """

    def snapshot(self) -> dict[str, Any]: ...

    def atomic_update(self, operation: Callable[[dict[str, Any]], T]) -> T: ...

    def reset(self) -> None: ...

# Interface tầng Business Domain Service
class RepositoryBase(ABC):

    @abstractmethod
    def get_assigned_cases_for_user(self, annotator_code: str) -> List[Dict[str, Any]]:
        """Lấy danh sách các record được gán cho user hiện tại (Reviewer page)."""
        pass

    @abstractmethod
    def save_draft(self, assignment_id: int, annotation_data: Dict[str, Any]) -> bool:
        """Lưu bản nháp annotation mà không khóa trạng thái."""
        pass

    @abstractmethod
    def submit_annotation(self, assignment_id: int, annotation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit annotation chính thức, validate C/S/A và kích hoạt chuyển đổi trạng thái (State machine)."""
        pass

    @abstractmethod
    def get_discussion_cases(self, annotator_code: str) -> List[Dict[str, Any]]:
        """Lấy danh sách các case cần thảo luận (Discussion page)."""
        pass

    @abstractmethod
    def submit_proposal(self, record_id: str, proposer_code: str, proposal: Dict[str, Any]) -> bool:
        """Tạo đề xuất resolution trong Discussion."""
        pass

    @abstractmethod
    def resolve_discussion(self, discussion_id: int, responder_code: str, action: str) -> bool:
        """Confirm hoặc Reject một proposal trong Discussion."""
        pass

    @abstractmethod
    def get_adjudication_cases(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các case leo thang cần Admin Phúc chốt (Adjudication page)."""
        pass

    @abstractmethod
    def submit_adjudication(self, record_id: str, admin_code: str, final_data: Dict[str, Any]) -> bool:
        """Admin đưa ra quyết định cuối cùng."""
        pass

    @abstractmethod
    def import_task06_bundle(self, records: List[Dict], predictions: List[Dict], routes: List[Dict]) -> Dict[str, int]:
        """Import bundle dữ liệu Task 06 (Idempotent)."""
        pass

    @abstractmethod
    def export_task07_bundle(self) -> Dict[str, Any]:
        """Xuất toàn bộ dữ liệu final corpus đạt chuẩn Task 07."""
        pass



