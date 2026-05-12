"""Orchestrate per-method explanation bundles (extend here for new methods)."""

from __future__ import annotations

from typing import Any

from .bazi import build_bazi_bundle
from .human_design import build_human_design_bundle
from .maya import build_maya_bundle
from .types import METHOD_EXPLANATION_VERSION
from .vedic import build_vedic_panchanga_bundle
from .western import build_western_tropical_bundle


def build_method_explanations(engine_json: dict[str, Any], *, locale: str = "nl-NL") -> dict[str, Any]:
    """
    Build structured explanations for each personal-reading method.

    Each bundle splits content into **headline** (what the chart states, using
    the same knowledge seeds as `interpretations.py`) and **personal_layer**
    (how this often shows up in lived experience). The UI/PDF can render them
    separately or merged.

    New methods: add a builder module, import it here, and register a key that
    matches `interpretations.py` / profile_book method ids where possible.
    """
    return {
        "western_tropical": build_western_tropical_bundle(engine_json, locale=locale),
        "vedic_panchanga": build_vedic_panchanga_bundle(engine_json, locale=locale),
        "chinese_ganzhi_bazi": build_bazi_bundle(engine_json, locale=locale),
        "human_design": build_human_design_bundle(engine_json, locale=locale),
        "maya": build_maya_bundle(engine_json, locale=locale),
        "_meta": {"version": METHOD_EXPLANATION_VERSION},
    }
