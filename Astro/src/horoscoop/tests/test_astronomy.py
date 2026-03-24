"""
Unit tests: coordinates, angular separation (no SE required for coord tests).
"""
import math
import pytest

from horoscoop import astronomy
from horoscoop import time_scales as ts


def test_ecliptic_to_equatorial_roundtrip():
    lon, lat = 45.0, 2.0
    eps = 23.44
    a, d = astronomy.ecliptic_to_equatorial_deg(lon, lat, eps)
    lon2, lat2 = astronomy.equatorial_to_ecliptic_deg(a, d, eps)
    assert abs(lon2 - lon) < 0.01
    assert abs(lat2 - lat) < 0.01


def test_solar_longitude_requires_se():
    jd_tt = 2451545.0
    lon, err = astronomy.solar_longitude_geocentric_deg(jd_tt)
    if err and "not installed" in str(err):
        pytest.skip("swisseph not installed")
    assert 0 <= lon < 360
