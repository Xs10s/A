"""
Unit tests: time scales. JD, Delta-T, TT/UT1, ERA, GMST, LST.
"""
from datetime import datetime, timezone
import math
import pytest

from horoscoop import time_scales as ts


def test_jd_from_datetime():
    # 2000-01-01 12:00 UTC ≈ JD 2451545.0 (UT1 convention)
    dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    jd = ts.jd_from_datetime(dt, "utc")
    assert abs(jd - 2451545.0) < 0.001


def test_normalize_angle_deg():
    assert ts.normalize_angle_deg(0) == 0
    assert ts.normalize_angle_deg(360) == 0
    assert ts.normalize_angle_deg(-90) == 270
    assert ts.normalize_angle_deg(400) == 40


def test_normalize_angle_rad():
    assert abs(ts.normalize_angle_rad(0) - 0) < 1e-10
    assert abs(ts.normalize_angle_rad(2 * math.pi) - 0) < 1e-10


def test_era():
    # ERA at J2000.0 UT1 should be in [0, 2π)
    jd = 2451545.0
    e = ts.era(jd)
    assert 0 <= e < 2 * math.pi


def test_tt_from_ut():
    jd_ut1 = 2451545.0
    dt = ts.delta_t(jd_ut1)
    jd_tt = ts.tt_from_ut(jd_ut1, dt)
    assert jd_tt > jd_ut1


def test_lst_deg():
    jd = 2451545.0
    lst = ts.lst_deg(jd, 0.0)
    assert 0 <= lst < 360
    lst2 = ts.lst_deg(jd, 15.0)
    assert abs((lst2 - lst) - 15.0) < 0.01 or abs((lst2 - lst) - 15.0 + 360) < 0.01


def test_delta_t_seconds_returns_source():
    sec, source = ts.delta_t_seconds(2451545.0)
    assert sec > 0
    assert source in ("swiss_ephemeris", "approximation")


def test_gmst_normalized():
    jd = 2451545.0
    g = ts.gmst_rad(jd)
    assert 0 <= g < 2 * math.pi


def test_gmst_increases_with_ut1():
    jd1 = 2451545.0
    jd2 = jd1 + 0.5
    g1 = ts.gmst_rad(jd1)
    g2 = ts.gmst_rad(jd2)
    assert g2 > g1 or (g2 < 0.1 and g1 > 6)  # wraparound
