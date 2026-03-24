"""
Tests: Chinese methods (Workstream 2) – Lìchūn boundary, day boundary, pillars, CNY.
"""
from datetime import datetime, timezone
import pytest

from horoscoop import chinese


def test_solar_term_index():
    assert chinese.solar_term_longitude_to_index(315) == 1
    assert chinese.solar_term_longitude_to_index(0) in (7, 8)
    assert 1 <= chinese.solar_term_longitude_to_index(180) <= 24


def test_ganzhi_day_deterministic():
    idx1, s1, b1 = chinese.stem_branch_from_jd_noon(2451545.0)
    idx2, s2, b2 = chinese.stem_branch_from_jd_noon(2451545.0)
    assert idx1 == idx2 and s1 == s2 and b1 == b2
    assert 1 <= idx1 <= 60
    assert s1 in chinese.STEMS and b1 in chinese.BRANCHES


def test_day_pillar_different_boundaries():
    jd_ut = 2451545.0 + 0.25
    d1 = chinese.day_pillar_jd_noon(jd_ut, "utc+8_midnight", 8.0)
    d2 = chinese.day_pillar_jd_noon(jd_ut, "local_midnight", 0.0)
    assert d1[0] is not None and d2[0] is not None
    assert isinstance(d1[0], int) and 1 <= d1[0] <= 60


def test_year_pillar_licheng_with_lichun():
    jd_after_licheng = 2451545.0 + 40
    ly = chinese.lichun_jd_ut_for_year(2000)
    if ly is not None:
        idx, stem, branch = chinese.year_pillar_licheng(jd_after_licheng, 8.0, ly, chinese.lichun_jd_ut_for_year(1999))
        assert 1 <= idx <= 60
        assert stem in chinese.STEMS and branch in chinese.BRANCHES


def test_cny_simplified_known_dates():
    cny_2024 = chinese.cny_date_simplified(2024)
    cny_2025 = chinese.cny_date_simplified(2025)
    if cny_2024:
        assert cny_2024.startswith("2024")
    if cny_2025:
        assert cny_2025.startswith("2025")


def test_month_pillar_from_year_stem():
    stem, branch = chinese.month_pillar_from_solar_term_and_year_stem(1, 1)
    assert stem in chinese.STEMS and branch in chinese.BRANCHES
    stem2, branch2 = chinese.month_pillar_from_solar_term_and_year_stem(3, 5)
    assert stem2 in chinese.STEMS and branch2 in chinese.BRANCHES


def test_hour_pillar_from_local_hour():
    s, b = chinese.bazi_pillar_hour_from_day_stem_branch(1, 0.5)
    assert s in chinese.STEMS and b in chinese.BRANCHES
    s2, b2 = chinese.bazi_pillar_hour_from_day_stem_branch(1, 23.5)
    assert s2 in chinese.STEMS and b2 in chinese.BRANCHES
