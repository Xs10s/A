"""Cache key construction.

De `profileHash` is deterministisch en stabiel over runs zolang alle
ingredienten gelijk blijven. Wijzigingen in glossary, formules of prompts
invalideren automatisch de cache via de versievelden.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable

from ..data.glossary.types import GLOSSARY_VERSION
from ..formulas.types import FORMULA_REGISTRY_VERSION
from ..interpretation.types import INTERPRETATION_BUILDER_VERSION
from ..narrative.prompts import PROMPT_VERSION
from ..relationships.types import RELATIONSHIP_MATRIX_VERSION
from ..values.types import VALUES_REGISTRY_VERSION


CACHE_VERSION = "1.0.0"


@dataclass(frozen=True)
class CacheKey:
    profile_hash: str
    inputs: dict[str, Any]
    versions: dict[str, str]


def _canonical(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _normalize_methods(methods: Iterable[str]) -> list[str]:
    return sorted({str(m).strip().lower() for m in methods if m})


def compute_profile_hash(
    *,
    birth_date: str | None,
    birth_time: str | None,
    birth_place: str | dict | None,
    timezone: Any | None = None,
    coordinates: dict | None = None,
    enabled_methods: Iterable[str] = (),
    llm_provider: str | None = None,
    llm_model: str | None = None,
    extra: dict | None = None,
) -> CacheKey:
    versions = {
        "cache": CACHE_VERSION,
        "glossary": GLOSSARY_VERSION,
        "formulas": FORMULA_REGISTRY_VERSION,
        "values": VALUES_REGISTRY_VERSION,
        "relationships": RELATIONSHIP_MATRIX_VERSION,
        "interpretation": INTERPRETATION_BUILDER_VERSION,
        "prompt": PROMPT_VERSION,
    }

    inputs: dict[str, Any] = {
        "birthDate": birth_date,
        "birthTime": birth_time,
        "birthPlace": birth_place,
        "timezone": timezone,
        "coordinates": coordinates,
        "enabledMethods": _normalize_methods(enabled_methods),
        "llm": {"provider": llm_provider or "null", "model": llm_model or ""},
        "extra": extra or {},
    }
    payload = {"inputs": inputs, "versions": versions}
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return CacheKey(profile_hash=digest, inputs=inputs, versions=versions)


def build_cache_key(**kwargs: Any) -> CacheKey:
    return compute_profile_hash(**kwargs)
