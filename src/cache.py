"""TTL + LRU cache for agent responses."""

from __future__ import annotations

import time
from collections import OrderedDict
from threading import Lock
from typing import Any


class TTLCache:
    def __init__(self, max_size: int = 128, ttl_seconds: float = 900.0) -> None:
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self.misses += 1
                return None
            created, value = entry
            if time.time() - created > self.ttl_seconds:
                del self._store[key]
                self.misses += 1
                return None
            self._store.move_to_end(key)
            self.hits += 1
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = (time.time(), value)
            self._store.move_to_end(key)
            while len(self._store) > self.max_size:
                self._store.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self.hits = 0
            self.misses = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


def make_key(question: str, history: list[dict[str, str]] | None = None) -> str:
    """Cache key from the normalized question text.

    Keyed on the question alone (case/whitespace-insensitive) so that asking the
    same question again is a cache hit regardless of the surrounding
    conversation. Trade-off: a context-dependent follow-up phrased with the exact
    same words as an earlier question would reuse the earlier answer — rare in
    practice, and callers can pass use_cache=False to bypass.
    """
    return " ".join(question.lower().split())
