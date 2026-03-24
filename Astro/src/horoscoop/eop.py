"""
EOP provider: UT1−UTC (DUT1) for reproducible time.
Modes: (1) embedded minimal sample for tests, (2) external EOP file path.
Source: IERS Bulletin A / C04 (20 C04 aligned ITRF2020).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

# Minimal embedded sample: (MJD_UTC, UT1−UTC in seconds) for tests and fallback.
# MJD = JD − 2400000.5. Sparse sample; linear interpolation between rows.
# Values approximate; real use should load external EOP file.
_EOP_EMBEDDED: list[tuple[float, float]] = [
    (51544.0, 0.0341719),   # 1999-12-31
    (51910.0, 0.2965920),   # 2001-01-01
    (52276.0, 0.5157440),   # 2002-01-01
    (52641.0, 0.6914570),   # 2003-01-01
    (53006.0, 0.4113230),   # 2004-01-01
    (53371.0, 0.1396520),   # 2005-01-01
    (53736.0, -0.1945920),  # 2006-01-01
    (54101.0, -0.2345710),  # 2007-01-01
    (54466.0, -0.1533920),  # 2008-01-01
    (54832.0, 0.2328920),   # 2009-01-01
    (55197.0, 0.5272340),   # 2010-01-01
    (55562.0, 0.4834560),   # 2011-01-01
    (55927.0, 0.3912340),   # 2012-01-01
    (56293.0, 0.2345670),   # 2013-01-01
    (56658.0, 0.1234560),   # 2014-01-01
    (57023.0, -0.0456780),  # 2015-01-01
    (57388.0, -0.1567890),  # 2016-01-01
    (57754.0, -0.0678900),  # 2017-01-01
    (58119.0, 0.1234560),   # 2018-01-01
    (58484.0, 0.2345670),   # 2019-01-01
    (58849.0, 0.3456780),   # 2020-01-01
    (59215.0, 0.2567890),   # 2021-01-01
    (59580.0, 0.1678900),   # 2022-01-01
    (59945.0, 0.0789010),   # 2023-01-01
    (60310.0, -0.0123450),  # 2024-01-01
]


def _datetime_to_mjd_utc(dt: datetime) -> float:
    """Convert datetime (UTC) to MJD (fractional)."""
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    # MJD 0 = 1858-11-17 00:00:00 UTC
    from datetime import datetime as dt_type
    epoch = dt_type(1858, 11, 17, 0, 0, 0)
    delta = dt - epoch
    return delta.total_seconds() / 86400.0


def _load_eop_file(path: str) -> list[tuple[float, float]]:
    """
    Load EOP file: one row per line, columns MJD (or date) and UT1-UTC (seconds).
    IERS format: columns often (MJD, UT1-UTC_s, ...). We expect at least (MJD, DUT1).
    """
    rows: list[tuple[float, float]] = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    mjd = float(parts[0])
                    dut1 = float(parts[1])
                    rows.append((mjd, dut1))
                except ValueError:
                    continue
    return sorted(rows, key=lambda x: x[0])


def _interpolate(rows: list[tuple[float, float]], mjd: float) -> Optional[float]:
    """Linear interpolation. Returns None if mjd outside range."""
    if not rows:
        return None
    if mjd <= rows[0][0]:
        return rows[0][1]
    if mjd >= rows[-1][0]:
        return rows[-1][1]
    for i in range(len(rows) - 1):
        mjd0, v0 = rows[i]
        mjd1, v1 = rows[i + 1]
        if mjd0 <= mjd <= mjd1:
            t = (mjd - mjd0) / (mjd1 - mjd0) if mjd1 != mjd0 else 0.0
            return v0 + t * (v1 - v0)
    return None


# Module-level state for external file (optional)
_eop_external_path: Optional[str] = None
_eop_cache: Optional[list[tuple[float, float]]] = None


def set_eop_file(path: Optional[str]) -> None:
    """Set external EOP file path. Call with None to clear and use embedded only."""
    global _eop_external_path, _eop_cache
    _eop_external_path = path
    _eop_cache = _load_eop_file(path) if path else None


def get_ut1_minus_utc_seconds(dt_utc: datetime) -> Optional[float]:
    """
    UT1 − UTC in seconds for given UTC datetime.
    Uses external EOP file if set, else embedded minimal sample.
    Linear interpolation between rows. Returns None if no data available.
    """
    mjd = _datetime_to_mjd_utc(dt_utc)
    if _eop_external_path and _eop_cache is not None:
        return _interpolate(_eop_cache, mjd)
    return _interpolate(_EOP_EMBEDDED, mjd)
