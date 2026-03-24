"""
Tests for presentation layer: ViewModel, diagnostics, SVG, PDF.
"""
from __future__ import annotations

import json
import pytest

from horoscoop import engine
from horoscoop.presentation import (
    build_view_model,
    normalize_diagnostics,
    render_wheel_svg,
    render_wheel_from_engine,
    render_pdf,
    format_degrees,
    sign_code_to_nl,
)


def test_viewmodel_date_only_input():
    """Date only input yields method availability flags and correct diagnostics aggregation."""
    out = engine.compute(birth_date="2000-01-01")
    vm = build_view_model(out)
    assert "input_summary" in vm
    assert vm["input_summary"]["completeness"]["has_date"] is True
    assert vm["input_summary"]["completeness"]["has_location"] is False
    assert vm["input_summary"]["completeness"]["has_timezone"] is False
    assert "diagnostics" in vm
    codes = vm["diagnostics"].get("codes", [])
    assert "NO_BIRTHTIME" in codes or "USED_DEFAULT_TIME" in codes or "NO_TIMEZONE" in codes
    assert "methods" in vm
    western_t = next(m for m in vm["methods"] if m["id"] == "western_tropical")
    assert western_t["available"] is False  # no location/timezone -> western is None
    vedic = next(m for m in vm["methods"] if m["id"] == "vedic_panchanga")
    assert vedic["available"] is True


def test_viewmodel_date_time_offset_no_location():
    """Date+time+offset, no location: planet table present, no houses."""
    out = engine.compute(
        birth_date="2000-01-01",
        birth_time_local="12:00:00",
        utc_offset_hours=1.0,
    )
    vm = build_view_model(out)
    western_t = next(m for m in vm["methods"] if m["id"] == "western_tropical")
    assert western_t["sections"]["planet_table"]
    assert western_t["sections"]["houses_table"] == []
    assert out["western"] is None


def test_svg_renders_valid_root():
    """SVG renderer produces valid SVG root element."""
    svg = render_wheel_svg({"Su": 110.0, "Mo": 45.0})
    assert "<svg" in svg
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg
    assert "</svg>" in svg


def test_svg_includes_12_sign_divisions():
    """SVG includes 12 zodiac sign divisions."""
    svg = render_wheel_svg({"Su": 0.0})
    count = svg.count('stroke="#888"')
    assert count >= 12


def test_svg_omits_houses_if_missing():
    """SVG omits house cusps when not provided."""
    svg_no_houses = render_wheel_svg({"Su": 100.0}, house_cusps_deg=None)
    svg_with_houses = render_wheel_svg(
        {"Su": 100.0},
        house_cusps_deg=[30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0, 0.0],
    )
    assert svg_no_houses.count('stroke="#444"') == 0
    assert svg_with_houses.count('stroke="#444"') >= 12


def test_pdf_returns_valid_bytes():
    """PDF returns bytes starting with %PDF and has substantial content."""
    out = engine.compute(
        birth_date="2000-01-01",
        birth_time_local="12:00:00",
        lat=52.0,
        lon=5.0,
        utc_offset_hours=1.0,
    )
    pdf_bytes = render_pdf(out)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500
    assert b"%%EOF" in pdf_bytes


def test_diagnostics_normalization():
    """Diagnostics normalize to codes, warnings, confidence_overall."""
    out = engine.compute(birth_date="2000-01-01", lat=52.0, lon=5.0)
    diag = normalize_diagnostics(out)
    assert "codes" in diag
    assert "warnings" in diag
    assert "confidence_overall" in diag
    assert isinstance(diag["warnings"], list)
    for w in diag["warnings"]:
        assert "code" in w or "label_nl" in w


def test_format_degrees():
    """Format degrees as DDD°MM′."""
    assert "110" in format_degrees(110.12)
    assert "°" in format_degrees(110.12)
    assert "′" in format_degrees(110.12)


def test_sign_code_to_nl():
    """Sign codes map to Dutch labels."""
    assert sign_code_to_nl("Aries") == "Ram"
    assert sign_code_to_nl("Cancer") == "Kreeft"
    assert sign_code_to_nl("Pisces") == "Vissen"


def test_render_wheel_from_engine_full():
    """Render wheel from full engine output (with western)."""
    out = engine.compute(
        birth_date="2000-01-01",
        birth_time_local="12:00:00",
        lat=52.0,
        lon=5.0,
        utc_offset_hours=1.0,
        house_system="P",
    )
    svg = render_wheel_from_engine(out, method_id="western_tropical")
    assert "<svg" in svg
    assert "Su" in svg or "Mo" in svg


def test_render_wheel_from_engine_sidereal():
    """Render sidereal wheel from engine."""
    out = engine.compute(
        birth_date="2000-01-01",
        birth_time_local="12:00:00",
        lat=52.0,
        lon=5.0,
        utc_offset_hours=1.0,
        house_system="P",
    )
    svg = render_wheel_from_engine(out, method_id="western_sidereal")
    assert "<svg" in svg


def test_viewmodel_tolerates_missing_fields():
    """ViewModel renders what's present; does not crash on missing fields."""
    minimal = {
        "meta": {"version": "1.0", "generated_at_utc": "2026-02-14T12:00:00Z", "engine": {}},
        "input": {"birth": {"date": "2000-01-01"}},
        "time": {"jd_tt": 2451545.0, "status": {}},
        "astronomy": {"bodies": {}},
        "western": None,
        "vedic": None,
        "chinese": None,
        "diagnostics": {"codes": []},
    }
    vm = build_view_model(minimal)
    assert vm["locale"] == "nl-NL"
    assert len(vm["methods"]) >= 4
