"""
Profile Cache
=============

Deterministische cache voor energieprofielen. De cache-key bevat:
    - geboortedatum, -tijd, -plaats
    - gekozen methodes (sorted)
    - glossaryVersion
    - formulaVersion (FORMULA_REGISTRY_VERSION)
    - valuesRegistryVersion
    - relationshipMatrixVersion
    - promptVersion
    - llm provider/model (zodat LLM-output niet over providers heen
      vermengd raakt)

Caches kunnen in-memory (test/dev) of op disk (productie) gehouden worden.
"""

from __future__ import annotations

from .keys import (
    CACHE_VERSION,
    CacheKey,
    build_cache_key,
    compute_profile_hash,
)
from .cache import (
    CacheBackend,
    DiskJsonCache,
    InMemoryCache,
    ProfileCache,
)

__all__ = [
    "CACHE_VERSION",
    "CacheKey",
    "CacheBackend",
    "DiskJsonCache",
    "InMemoryCache",
    "ProfileCache",
    "build_cache_key",
    "compute_profile_hash",
]
