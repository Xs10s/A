"""Tests for the Maya time-cycle engine."""
from __future__ import annotations

import pytest

from horoscoop import engine, maya


def test_long_count_zero_at_correlation():
    bk, kt, tn, un, ki = maya.long_count_from_jd(maya.DEFAULT_CORRELATION)
    assert (bk, kt, tn, un, ki) == (0, 0, 0, 0, 0)


def test_kin_at_correlation_is_anchor():
    """At JD == correlation, kin should be the GMT anchor (160 = 4 Ahau)."""
    kin = maya.kin_from_jd(float(maya.DEFAULT_CORRELATION))
    assert kin == maya.ANCHOR_KIN_AT_GMT
    tone, sign = maya.tzolkin_from_kin(kin)
    assert tone == 4
    assert sign == 20  # Ahau


def test_haab_at_correlation_is_8_cumku():
    """At JD == correlation, Haab should be 8 Cumku (month index 17)."""
    day, m_idx, m_name = maya.haab_from_jd(float(maya.DEFAULT_CORRELATION))
    assert m_name == "Kumk'u"
    assert m_idx == 17
    assert day == 7  # 0-based: day=7 means the 8th day


def test_kin_cycles_after_260_days():
    base = float(maya.DEFAULT_CORRELATION)
    assert maya.kin_from_jd(base) == maya.kin_from_jd(base + 260.0)


def test_haab_cycles_after_365_days():
    base = float(maya.DEFAULT_CORRELATION)
    h0 = maya.haab_from_jd(base)
    h1 = maya.haab_from_jd(base + 365.0)
    assert h0 == h1


def test_wavespell_structure():
    info = maya.wavespell_info(1)  # Magnetic Dragon
    assert info["wavespell_index"] == 1
    assert info["wavespell_position"] == 1
    assert info["wavespell_kin_leader"] == 1
    castle = info["castle"]
    assert castle["id"] == 1


def test_wavespell_info_at_kin_260():
    info = maya.wavespell_info(260)
    assert info["wavespell_position"] == 13  # Cosmic
    assert info["wavespell_index"] == 20


def test_build_maya_via_engine():
    out = engine.compute(
        birth_date="1990-06-15",
        birth_time_local="10:30:00",
        lat=52.0,
        lon=5.0,
        utc_offset_hours=2.0,
    )
    maya_out = out["maya"]
    assert maya_out["status"]["computed"] is True
    assert 1 <= maya_out["kin"] <= 260
    assert "tone" in maya_out
    assert "sign" in maya_out
    assert maya_out["long_count"]["label"]
    assert maya_out["haab"]["label"]


def test_personal_year_cycles_progression():
    out = engine.compute(birth_date="1990-06-15", utc_offset_hours=0)
    cycles = out["maya"]["personal_year_cycles"]
    # 4 cycles, all distinct kin numbers (or at least correct count).
    assert len(cycles) == 4
    assert all(1 <= c["kin"] <= 260 for c in cycles)
