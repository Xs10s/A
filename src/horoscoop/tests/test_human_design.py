"""Tests for the Human Design engine."""
from __future__ import annotations

import pytest

from horoscoop import engine, human_design


def test_gate_line_from_longitude_anchor():
    # Anchor: gate 41 starts at 302.25 deg
    g, line, _, _ = human_design.gate_line_from_longitude(302.25)
    assert g == 41
    assert line == 1


def test_gate_line_wraps_around():
    # 302.25 + 64 * 5.625 = 360 + 302.25 -> back to gate 41
    g, _, _, _ = human_design.gate_line_from_longitude(302.25 + 64 * human_design.GATE_DEG)
    assert g == 41


def test_gate_line_increments_through_wheel():
    # Moving forward by gate width should give the next gate in the wheel order.
    g0, _, _, _ = human_design.gate_line_from_longitude(302.25 + 0.1)
    g1, _, _, _ = human_design.gate_line_from_longitude(302.25 + human_design.GATE_DEG + 0.1)
    assert g0 == 41
    assert g1 == 19


def test_centers_and_channels_consistency():
    # All channel gates should be in GATE_CENTER mapping (or DUAL_CENTER_GATES).
    for ch in human_design.CHANNELS:
        a, b = ch["gates"]
        assert a in human_design.GATE_CENTER or a in human_design.DUAL_CENTER_GATES
        assert b in human_design.GATE_CENTER or b in human_design.DUAL_CENTER_GATES


def test_build_human_design_unavailable_without_jd():
    block = human_design.build_human_design(None)
    assert block["status"]["computed"] is False
    assert block["type"] is None


def test_build_human_design_full_chart():
    """Integration smoke: through the engine."""
    out = engine.compute(
        birth_date="1990-06-15",
        birth_time_local="10:30:00",
        lat=52.0,
        lon=5.0,
        utc_offset_hours=2.0,
    )
    hd = out["human_design"]
    assert hd["status"]["computed"] is True
    # Type must be one of the canonical 5 (we expect a non-Reflector for most birth times).
    assert hd["type"] in {"Generator", "Manifesting Generator", "Manifestor", "Projector", "Reflector"}
    assert hd["authority"] in {"Emotional", "Sacral", "Splenic", "Ego", "Self-projected", "Mental", "Lunar"}
    assert hd["profile"]["value"] is not None
    # Active gates should be at least the bodies x charts (some duplicates likely).
    assert len(hd["active_gates"]) >= 5
    # Personality + design must contain Sun and Earth.
    assert "Sun" in hd["personality"]
    assert "Earth" in hd["personality"]
    assert "Sun" in hd["design"]
    assert "Earth" in hd["design"]
    # Earth gate should be exactly opposite Sun gate (180 deg).
    sun_p = hd["personality"]["Sun"]["lon_deg"]
    earth_p = hd["personality"]["Earth"]["lon_deg"]
    diff = abs(((sun_p - earth_p) % 360) - 180.0)
    assert diff < 1e-6


def test_design_chart_is_88_solar_arc_before():
    """Verify design Sun is exactly 88 degrees behind personality Sun."""
    out = engine.compute(
        birth_date="1990-06-15",
        birth_time_local="10:30:00",
        lat=52.0,
        lon=5.0,
        utc_offset_hours=2.0,
    )
    hd = out["human_design"]
    sun_pers = hd["personality"]["Sun"]["lon_deg"]
    sun_des = hd["design"]["Sun"]["lon_deg"]
    arc = (sun_pers - sun_des) % 360.0
    # Should be very close to 88
    assert abs(arc - 88.0) < 1e-3
