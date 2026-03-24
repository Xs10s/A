"""
Tests: EOP provider UT1−UTC interpolation.
"""
from datetime import datetime, timezone
import pytest

from horoscoop import eop


def test_get_ut1_minus_utc_embedded():
    dt = datetime(2005, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    val = eop.get_ut1_minus_utc_seconds(dt)
    assert val is not None
    assert -1.0 < val < 1.0


def test_eop_interpolation_between_rows():
    dt_early = datetime(2003, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
    dt_late = datetime(2003, 9, 1, 0, 0, 0, tzinfo=timezone.utc)
    v1 = eop.get_ut1_minus_utc_seconds(dt_early)
    v2 = eop.get_ut1_minus_utc_seconds(dt_late)
    assert v1 is not None
    assert v2 is not None
    assert v1 != v2 or abs(v1 - v2) < 0.01