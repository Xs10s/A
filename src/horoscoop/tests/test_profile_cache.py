from __future__ import annotations

import os

from horoscoop.profile_cache import (
    DiskJsonCache,
    InMemoryCache,
    ProfileCache,
    build_cache_key,
    compute_profile_hash,
)


def _common_args() -> dict:
    return {
        "birth_date": "2000-01-01",
        "birth_time": "12:00",
        "birth_place": {"lat": 52.0, "lon": 5.0},
        "timezone": 1.0,
        "coordinates": {"lat": 52.0, "lon": 5.0},
        "enabled_methods": ["western", "vedic"],
        "llm_provider": "null",
        "llm_model": "",
    }


def test_profile_hash_deterministic():
    a = compute_profile_hash(**_common_args())
    b = compute_profile_hash(**_common_args())
    assert a.profile_hash == b.profile_hash


def test_profile_hash_changes_with_method_set():
    base = compute_profile_hash(**_common_args())
    args = _common_args()
    args["enabled_methods"] = ["western", "bazi"]
    other = compute_profile_hash(**args)
    assert base.profile_hash != other.profile_hash


def test_profile_hash_method_order_irrelevant():
    args1 = _common_args()
    args1["enabled_methods"] = ["western", "vedic"]
    args2 = _common_args()
    args2["enabled_methods"] = ["vedic", "western"]
    a = compute_profile_hash(**args1)
    b = compute_profile_hash(**args2)
    assert a.profile_hash == b.profile_hash


def test_profile_hash_changes_with_llm_provider():
    args = _common_args()
    a = compute_profile_hash(**args)
    args["llm_provider"] = "ollama"
    b = compute_profile_hash(**args)
    assert a.profile_hash != b.profile_hash


def test_in_memory_cache_set_and_get():
    cache = ProfileCache(InMemoryCache())
    key = build_cache_key(**_common_args())
    assert cache.get_profile(key) is None
    cache.set(key, {"intro": {"text": "hello"}})
    assert cache.has(key) is True
    assert cache.get_profile(key) == {"intro": {"text": "hello"}}


def test_disk_json_cache_round_trip(tmp_path):
    cache = ProfileCache(DiskJsonCache(str(tmp_path)))
    key = build_cache_key(**_common_args())
    cache.set(key, {"summary": {"text": "ok"}})
    assert cache.get_profile(key) == {"summary": {"text": "ok"}}
    assert os.path.exists(os.path.join(str(tmp_path), f"{key.profile_hash}.json"))


def test_disk_json_cache_invalidate(tmp_path):
    cache = ProfileCache(DiskJsonCache(str(tmp_path)))
    key = build_cache_key(**_common_args())
    cache.set(key, {"x": 1})
    cache.invalidate(key)
    assert cache.get_profile(key) is None
