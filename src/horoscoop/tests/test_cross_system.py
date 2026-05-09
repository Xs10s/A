"""Tests for the cross-system intelligence layer."""
from __future__ import annotations

from horoscoop import engine
from horoscoop.cross_system import (
    build_cross_system,
    element_resonance,
    polarity_resonance,
)
from horoscoop.energy_profile import build_combined_energy_profile


def _sample_engine_output():
    return engine.compute(
        birth_date="1990-06-15",
        birth_time_local="10:30:00",
        lat=52.0,
        lon=5.0,
        utc_offset_hours=2.0,
    )


def test_element_resonance_returns_systems():
    out = _sample_engine_output()
    res = element_resonance(out)
    assert "systems" in res
    assert set(res["systems"].keys()) == {"western", "bazi", "maya", "hd"}
    assert "agreement_score" in res


def test_polarity_resonance_yang_or_yin():
    out = _sample_engine_output()
    pol = polarity_resonance(out)
    assert "sources" in pol
    assert pol["dominant"] in {"yang", "yin", "balanced", None}


def test_build_cross_system_full():
    out = _sample_engine_output()
    cs = build_cross_system(out, locale="nl-NL")
    assert "summary" in cs
    keys = {s["key"] for s in cs["sections"]}
    assert keys == {"element_resonance", "polarity_resonance", "decision_resonance", "timing_resonance"}
    assert cs["convergence"]["element"] in {"fire", "earth", "air", "water", "wood", "metal", None}


def test_combined_profile_includes_hd_and_maya():
    out = _sample_engine_output()
    combined = build_combined_energy_profile(out, locale="nl-NL")
    sys_ids = combined["systems"]
    assert "human_design" in sys_ids
    assert "maya" in sys_ids


def test_build_cross_system_works_without_time():
    """When time is missing, HD is unavailable but cross-system should still
    produce a valid output (other systems still contribute)."""
    out = engine.compute(
        birth_date="1990-06-15",
        utc_offset_hours=0,
    )
    cs = build_cross_system(out)
    assert "summary" in cs
    # Maya works without time:
    assert out["maya"]["status"]["computed"] is True
