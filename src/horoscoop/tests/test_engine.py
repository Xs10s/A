"""
Integration: engine.compute returns valid structure (no SE required for structure check).
"""
import pytest

from horoscoop import engine
from horoscoop import jyotish_chart as jc


def test_compute_structure():
    out = engine.compute(
        birth_date="2000-01-01",
        birth_time_local="12:00:00",
        lat=52.0,
        lon=5.0,
        utc_offset_hours=1.0,
        house_system="P",
    )
    assert "meta" in out
    assert "version" in out["meta"]
    assert "input" in out
    assert "time" in out
    assert "astronomy" in out
    assert "western" in out or "vedic" in out
    assert "vedic" in out
    assert "chinese" in out
    assert out["time"]["jd_tt"] is not None
    assert "delta_t_source" in out["time"]
    assert "ut1_utc_source" in out["time"]
    vedic = out.get("vedic") or {}
    jy = vedic.get("jyotish") or {}
    assert jy.get("status", {}).get("house_model") == "whole_sign_from_sidereal_lagna"
    grahas = jy.get("grahas") or []
    sun = next((g for g in grahas if g.get("name_en") == "Sun"), None)
    assert sun and sun.get("rashi")
    assert sun.get("house") is not None
    assert len(jy.get("d1_bhavas") or []) == 12
    assert isinstance(sun.get("natural_dignity"), dict)
    assert sun["natural_dignity"].get("rashilord_en")
    assert sun["natural_dignity"]["code"] in (
        "exalted",
        "debilitated",
        "own",
        "mulatrikona",
        "mitra_sign_lord",
        "sama_sign_lord",
        "satru_sign_lord",
    )
    assert isinstance(sun.get("bhava_groups"), list)
    assert isinstance(sun.get("vargas"), dict)
    assert "D9" in sun["vargas"] and sun["vargas"]["D9"].get("rashi")
    assert sun["vargas"]["D9"].get("house") is not None
    divs = (jy.get("divisional_charts") or {})
    assert set(divs.keys()) == set(jc.SHODASHA_VARGA_IDS)


def test_compute_no_place():
    out = engine.compute(
        birth_date="1990-06-15",
        birth_time_local="14:30:00",
        utc_offset_hours=0,
    )
    assert "time" in out and out["time"].get("jd_tt") is not None
    assert out["western"] is None


def test_naive_dt_no_tz_warnings_no_houses():
    out = engine.compute(
        birth_date="2000-01-01",
        birth_time_local="12:00:00",
        lat=52.0,
        lon=5.0,
    )
    assert "diagnostics" in out
    assert "NO_TIMEZONE" in out["diagnostics"].get("codes", [])
    assert out["western"] is None
    warnings = (out.get("time") or {}).get("status") or {}
    warnings = warnings.get("warnings") or []
    assert any("NO_TIMEZONE" in w for w in warnings)


def test_tz_aware_correct_path():
    out = engine.compute(
        birth_date="2000-01-01",
        birth_time_local="12:00:00",
        lat=52.0,
        lon=5.0,
        utc_offset_minutes=60,
        house_system="P",
    )
    assert out["time"].get("datetime_local") is not None
    assert "NO_TIMEZONE" not in out["diagnostics"].get("codes", [])


def test_ut1_utc_fallback_labeled():
    out = engine.compute(
        birth_date="2000-01-01",
        birth_time_local="12:00:00",
        utc_offset_hours=0,
    )
    assert out["time"]["ut1_utc_source"] in ("eop", "assumed_zero")
    assert "delta_t_source" in out["time"]
