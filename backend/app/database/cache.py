"""Lightweight caching layer for weather and geocoding responses.

Provides time-to-live (TTL) expiration to avoid redundant external network requests,
respect provider rate limits, and deliver sub-10ms cached responses.
"""

import time
from typing import Any, Dict, Optional
import threading


class CacheEntry:
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class WeatherCache:
    def __init__(self):
        self._store: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if entry.is_expired():
                del self._store[key]
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int = 900) -> None:
        with self._lock:
            self._store[key] = CacheEntry(value, ttl_seconds)

    def delete(self, key: str) -> None:
        with self._lock:
            if key in self._store:
                del self._store[key]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def size(self) -> int:
        with self._lock:
            now = time.time()
            # Clean expired on query
            self._store = {k: v for k, v in self._store.items() if v.expires_at > now}
            return len(self._store)


# Global singleton instance
weather_cache = WeatherCache()
