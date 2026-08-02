from __future__ import annotations

import copy
import json
import os
import threading
from pathlib import Path
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class FakeRepository:
    """JSON-backed mock repository with atomic replace and optimistic versions."""

    def __init__(self, path: str | Path, seed_factory: Callable[[], dict[str, Any]]):
        self.path = Path(path)
        self.seed_factory = seed_factory
        self._lock = threading.RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(seed_factory())

    def _read(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict[str, Any]) -> None:
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temp, self.path)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return copy.deepcopy(self._read())

    def atomic_update(self, operation: Callable[[dict[str, Any]], T]) -> T:
        with self._lock:
            data = self._read()
            result = operation(data)
            self._write(data)
            return result

    def reset(self) -> None:
        with self._lock:
            self._write(self.seed_factory())

