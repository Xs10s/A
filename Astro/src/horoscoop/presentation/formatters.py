"""
nl-NL formatters: degrees, datetime, orb, sign labels.
"""
from __future__ import annotations

from typing import Optional

# Sign codes (Aries..Pisces) -> nl-NL labels (Ram..Vissen)
SIGN_CODES: list[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_LABELS_NL = [
    "Ram", "Stier", "Tweelingen", "Kreeft", "Leeuw", "Maagd",
    "Weegschaal", "Schorpioen", "Boogschutter", "Steenbok", "Waterman", "Vissen",
]
SIGN_TO_NL: dict[str, str] = dict(zip(SIGN_CODES, SIGN_LABELS_NL))

# Body IDs -> nl-NL labels (2-letter for wheel; full for tables)
BODY_LABELS_NL: dict[str, str] = {
    "Sun": "Zon", "Moon": "Maan", "Mercury": "Mercurius",
    "Venus": "Venus", "Mars": "Mars", "Jupiter": "Jupiter", "Saturn": "Saturn",
}
BODY_2LETTER: dict[str, str] = {
    "Sun": "Su", "Moon": "Mo", "Mercury": "Me", "Venus": "Ve",
    "Mars": "Ma", "Jupiter": "Ju", "Saturn": "Sa",
}


def sign_code_to_nl(sign_code: str) -> str:
    """Map Aries..Pisces to Ram..Vissen."""
    return SIGN_TO_NL.get(sign_code, sign_code)


def format_degrees(
    deg: float,
    *,
    include_seconds: bool = False,
    decimal_minutes: bool = False,
) -> str:
    """
    Format degrees as DDD°MM′ or DDD°MM′SS″.
    Default: DDD°MM′ (minutes); include_seconds for detail view.
    """
    if deg is None:
        return "n.v.t."
    d = float(deg)
    dd = int(d) % 360
    frac = d - int(d)
    mm_float = frac * 60.0
    mm = int(mm_float)
    if include_seconds:
        ss_float = (mm_float - mm) * 60.0
        ss = int(round(ss_float))
        if ss >= 60:
            ss, mm = 0, mm + 1
        if mm >= 60:
            mm, dd = 0, dd + 1
        return f"{dd}°{mm:02d}′{ss:02d}″"
    if decimal_minutes:
        return f"{dd}°{mm_float:.2f}′"
    return f"{dd}°{mm:02d}′"


def format_orb(orb_deg: float, applying: bool) -> str:
    """Format orb as DDD°MM′ + applying/separating label."""
    base = format_degrees(orb_deg)
    suffix = " (applicerend)" if applying else " (separerend)"
    return base + suffix


def format_datetime_nl(iso_str: Optional[str], zone_label: Optional[str] = None) -> str:
    """
    Convert ISO-8601 to nl-NL: "14 feb 2026 13:22" + optional zone label.
    """
    if not iso_str:
        return "niet opgegeven"
    try:
        from datetime import datetime
        if "T" in iso_str:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        else:
            return iso_str
        months_nl = ["jan", "feb", "mrt", "apr", "mei", "jun",
                     "jul", "aug", "sep", "okt", "nov", "dec"]
        result = f"{dt.day} {months_nl[dt.month - 1]} {dt.year} {dt.hour:02d}:{dt.minute:02d}"
        if zone_label:
            result += f" ({zone_label})"
        return result
    except Exception:
        return iso_str


def format_jd(jd: Optional[float]) -> str:
    """JD rounded to 6 decimals."""
    if jd is None:
        return "n.v.t."
    return f"{jd:.6f}"


def format_delta_t(dt_sec: Optional[float]) -> str:
    """ΔT rounded to 0.1s."""
    if dt_sec is None:
        return "n.v.t."
    return f"{dt_sec:.1f}s"
