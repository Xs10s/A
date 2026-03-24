"""
Unit tests: tropical ↔ sidereal, ayanamsha subtraction.
"""
import pytest

from horoscoop import sidereal


def test_tropical_to_sidereal():
    sid = sidereal.tropical_to_sidereal_deg(30.0, 24.0)
    assert abs(sid - 6.0) < 0.01 or abs(sid - (6.0 + 360)) < 0.01


def test_sidereal_to_tropical_roundtrip():
    trop = 100.0
    aya = 24.0
    sid = sidereal.tropical_to_sidereal_deg(trop, aya)
    trop2 = sidereal.sidereal_to_tropical_deg(sid, aya)
    assert abs(trop2 % 360 - trop % 360) < 0.01
