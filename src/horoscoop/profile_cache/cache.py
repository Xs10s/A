"""Cache backends and ProfileCache wrapper.

Twee backends:
    - InMemoryCache: snel, niet-persistent (test/dev).
    - DiskJsonCache: een file per profileHash onder een cache-folder
      (productie).

De `ProfileCache` is dun en gebruikt een `CacheBackend`-protocol zodat
de keuze later eenvoudig uitbreidbaar blijft.
"""

from __future__ import annotations

import json
import os
import threading
from typing import Any, Iterator, Protocol

from .keys import CacheKey


class CacheBackend(Protocol):
    def get(self, key: str) -> dict | None: ...
    def set(self, key: str, value: dict) -> None: ...
    def delete(self, key: str) -> None: ...
    def keys(self) -> Iterator[str]: ...


class InMemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> dict | None:
        with self._lock:
            data = self._store.get(key)
            return None if data is None else dict(data)

    def set(self, key: str, value: dict) -> None:
        with self._lock:
            self._store[key] = dict(value)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def keys(self) -> Iterator[str]:
        with self._lock:
            return iter(list(self._store.keys()))


class DiskJsonCache:
    def __init__(self, directory: str) -> None:
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
        self._lock = threading.RLock()

    def _path_for(self, key: str) -> str:
        return os.path.join(self.directory, f"{key}.json")

    def get(self, key: str) -> dict | None:
        path = self._path_for(key)
        if not os.path.exists(path):
            return None
        with self._lock:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                return None

    def set(self, key: str, value: dict) -> None:
        path = self._path_for(key)
        with self._lock:
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(value, f, ensure_ascii=False, indent=2, sort_keys=True)
            os.replace(tmp, path)

    def delete(self, key: str) -> None:
        path = self._path_for(key)
        if os.path.exists(path):
            with self._lock:
                try:
                    os.remove(path)
                except OSError:
                    pass

    def keys(self) -> Iterator[str]:
        for name in os.listdir(self.directory):
            if name.endswith(".json"):
                yield name[:-5]


class ProfileCache:
    """High-level interface used by the engine."""

    def __init__(self, backend: CacheBackend | None = None) -> None:
        self.backend: CacheBackend = backend or InMemoryCache()

    def get(self, key: CacheKey) -> dict | None:
        return self.backend.get(key.profile_hash)

    def set(self, key: CacheKey, profile: dict) -> None:
        envelope = {
            "profileHash": key.profile_hash,
            "inputs": key.inputs,
            "versions": key.versions,
            "profile": profile,
        }
        self.backend.set(key.profile_hash, envelope)

    def get_profile(self, key: CacheKey) -> dict | None:
        envelope = self.get(key)
        if envelope is None:
            return None
        return envelope.get("profile")

    def has(self, key: CacheKey) -> bool:
        return self.backend.get(key.profile_hash) is not None

    def invalidate(self, key: CacheKey) -> None:
        self.backend.delete(key.profile_hash)
