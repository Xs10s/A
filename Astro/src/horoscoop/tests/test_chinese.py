"""
Unit tests: Ganzhi index, stem/branch, solar term index.
"""
import pytest

from horoscoop import chinese


def test_sexagenary_index():
    idx = chinese.ganzhi_index_from_jd_noon(2451545.0)
    assert 1 <= idx <= 60


def test_stem_branch():
    stem, branch = chinese.stem_branch_from_sexagenary_index(1)
    assert stem in chinese.STEMS
    assert branch in chinese.BRANCHES


def test_solar_term_longitude():
    idx = chinese.solar_term_longitude_to_index(315)
    assert idx >= 1 and idx <= 24


def test_hour_branch():
    # Local 23:00–01:00 = zǐ = 0
    hb = chinese.hour_branch_from_utc_hour(15.0, 8.0)  # 23:00 local
    assert 0 <= hb <= 11
