from __future__ import annotations

from typing import Any, Callable, Protocol, TypeVar

T = TypeVar("T")


class Repository(Protocol):
    """Interface Nga and Ngoc agree on for UI/persistence integration.

    A real adapter must provide snapshot reads and serializable atomic updates.
    The callback receives the complete normalized store and must either finish
    successfully or raise, in which case no state is committed.
    """

    def snapshot(self) -> dict[str, Any]: ...

    def atomic_update(self, operation: Callable[[dict[str, Any]], T]) -> T: ...

    def reset(self) -> None: ...

