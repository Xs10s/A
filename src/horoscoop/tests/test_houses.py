"""
Unit tests: house_from_cusps (no SE required).
"""
import pytest

from horoscoop import houses
from horoscoop import time_scales as ts


def test_house_from_cusps():
    # Equal house style: cusps 0, 30, 60, ... (index 1..12)
    cusps = [0.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0]
    assert houses.house_from_cusps(15.0, cusps) == 1
    assert houses.house_from_cusps(45.0, cusps) == 2
    assert houses.house_from_cusps(350.0, cusps) == 12  # wraparound
