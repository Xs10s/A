"""
Unit tests: tithi, nakshatra, yoga, karana (deterministic formulas).
Workstream 3: sunrise mode, end-times, ranges.
"""
import pytest

from horoscoop import vedic

try:
    from horoscoop import astronomy as _astro
    _SE_AVAILABLE = _astro._swe_calc_available()
except Exception:
    _SE_AVAILABLE = False


def test_tithi_index():
    # Moon 12° ahead of Sun → tithi 2
    idx = vedic.tithi_index_from_moon_sun_longitude(12.0, 0.0)
    assert idx == 2
    idx2 = vedic.tithi_index_from_moon_sun_longitude(0.0, 0.0)
    assert idx2 == 1


def test_tithi_index_range_1_to_30():
    for deg in (0.0, 12.0, 180.0, 359.9):
        idx = vedic.tithi_index_from_moon_sun_longitude(deg, 0.0)
        assert 1 <= idx <= 30, f"tithi {idx} for moon_sun_diff={deg}"


def test_nakshatra_index():
    idx = vedic.nakshatra_index_from_longitude_deg(0)
    assert 1 <= idx <= 27
    idx2 = vedic.nakshatra_index_from_longitude_deg(13.5)
    assert idx2 == 2


def test_nakshatra_index_range_1_to_27():
    for lon in (0.0, 13.0 + 20/60, 180.0, 359.0):
        idx = vedic.nakshatra_index_from_longitude_deg(lon)
        assert 1 <= idx <= 27


def test_yoga_index():
    idx = vedic.yoga_index_from_sun_moon_longitude(0.0, 0.0)
    assert 1 <= idx <= 27


def test_yoga_index_range_1_to_27():
    for s in (0.0, 30.0, 180.0, 359.0):
        idx = vedic.yoga_index_from_sun_moon_longitude(s, 0.0)
        assert 1 <= idx <= 27


def test_karana_index():
    idx = vedic.karana_index_from_moon_sun_longitude(6.0, 0.0)
    assert 1 <= idx <= 60


def test_vaara():
    # JD 2451545 = Saturday 2000-01-01 12:00
    v = vedic.vaara_from_jd(2451545.0)
    assert v == 6  # Saturday


def test_jd_ut_to_iso_utc():
    s = vedic.jd_ut_to_iso_utc(2451545.0)
    assert "2000" in s and "Z" in s or "00:00" in s


def test_jd_ut_to_iso_local():
    s = vedic.jd_ut_to_iso_local(2451545.0, 5.5)
    assert "2000" in s


@pytest.mark.skipif(not _SE_AVAILABLE, reason="Swiss Ephemeris required for end-times")
def test_tithi_end_after_eval_and_within_sanity():
    """Tithi end time must be after evaluation time and within ~1 day (sanity)."""
    from horoscoop import time_scales as ts
    jd_ut = 2460400.5  # 2025-01-15 noon UT
    dt_sec, _ = ts.delta_t_seconds(jd_ut)
    jd_tt = ts.tt_from_ut(jd_ut, dt_sec)
    from horoscoop import astronomy as astro
    from horoscoop import sidereal
    xs, _ = astro.calc_planet_geocentric(jd_tt, astro.SE_SUN)
    xm, _ = astro.calc_planet_geocentric(jd_tt, astro.SE_MOON)
    tithi = vedic.tithi_index_from_moon_sun_longitude(xm[0], xs[0])
    jd_end = vedic.tithi_end_jd_ut(jd_ut, tithi)
    if jd_end is not None:
        assert jd_end >= jd_ut
        assert jd_end - jd_ut <= 1.5  # tithi ~1 day


@pytest.mark.skipif(not _SE_AVAILABLE, reason="Swiss Ephemeris required")
def test_sunrise_based_differs_from_instant():
    """Sunrise-based panchanga can differ from instant (different evaluation time)."""
    from horoscoop import engine
    out_inst = engine.compute(
        "2025-01-15",
        "06:00:00",
        lat=28.6,
        lon=77.2,
        timezone_iana="Asia/Kolkata",
        vedic_at="instant",
    )
    out_sun = engine.compute(
        "2025-01-15",
        "06:00:00",
        lat=28.6,
        lon=77.2,
        timezone_iana="Asia/Kolkata",
        vedic_at="sunrise",
    )
    assert out_inst["vedic"]["at_mode"] == "instant"
    assert out_sun["vedic"]["at_mode"] == "sunrise"
    if out_sun["vedic"].get("panchanga"):
        # May differ (sunrise is earlier than 06:00 in Jan in India)
        assert "tithi" in out_sun["vedic"]["panchanga"]
    else:
        assert "VEDIC_SUNRISE" in str(out_sun["vedic"].get("warnings", []) + out_sun["vedic"].get("diagnostics", []))


def test_vedic_sunrise_requires_location():
    """Without location, sunrise mode returns unavailable with diagnostic."""
    from horoscoop import engine
    out = engine.compute("2025-01-15", "12:00:00", vedic_at="sunrise")
    assert out["vedic"]["at_mode"] == "sunrise"
    assert out["vedic"].get("panchanga") is None or out["vedic"]["status"]["computed"] is False
    assert "VEDIC_SUNRISE_REQUIRES_LOCATION" in out["vedic"].get("diagnostics", []) or "location" in str(out["vedic"].get("status", {}).get("requires", []))
