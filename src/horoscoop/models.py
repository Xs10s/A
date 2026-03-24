"""
Data models: typed value wrappers with unit, frame, method, confidence.
Layer C / output contracts. No computation logic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Optional, Sequence

# -----------------------------------------------------------------------------
# Quality / status enums
# -----------------------------------------------------------------------------


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ESTIMATED = "estimated"
    UNAVAILABLE = "unavailable"


class Requires(str, Enum):
    DATE = "date"
    TIME = "time"
    LATLON = "latlon"
    TIMEZONE = "timezone"
    EOP_DATA = "eop_data"


# -----------------------------------------------------------------------------
# Typed value: value + unit + frame + method + confidence
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class TypedValue:
    """Every computed value: value, unit, frame, method, confidence."""

    value: float | int | str | bool
    unit: str
    frame: str
    method: str
    confidence: Confidence

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "unit": self.unit,
            "frame": self.frame,
            "method": self.method,
            "confidence": self.confidence.value,
        }


# -----------------------------------------------------------------------------
# Status block (uniform in each output block)
# -----------------------------------------------------------------------------


@dataclass
class BlockStatus:
    computed: bool
    requires: list[Requires]
    confidence: Confidence
    assumptions: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "computed": self.computed,
            "requires": [r.value for r in self.requires],
            "confidence": self.confidence.value,
            "assumptions": self.assumptions,
            "warnings": self.warnings,
        }


# -----------------------------------------------------------------------------
# Input
# -----------------------------------------------------------------------------


@dataclass
class BirthPlace:
    lat: Optional[float] = None   # deg WGS84
    lon: Optional[float] = None   # deg WGS84
    elevation_m: Optional[float] = None


@dataclass
class BirthInput:
    date: str  # YYYY-MM-DD
    time_local: Optional[str] = None  # HH:MM:SS
    place: Optional[BirthPlace] = None
    timezone_iana: Optional[str] = None


# -----------------------------------------------------------------------------
# Time block
# -----------------------------------------------------------------------------


@dataclass
class TimeBlock:
    datetime_utc: Optional[str] = None  # ISO-8601
    jd_ut1: Optional[float] = None      # days
    jd_tt: Optional[float] = None       # days
    jd_tdb: Optional[float] = None      # days
    delta_t_seconds: Optional[float] = None
    ut1_utc_seconds: Optional[float] = None
    status: Optional[BlockStatus] = None


# -----------------------------------------------------------------------------
# Astronomy body entry
# -----------------------------------------------------------------------------


class FrameEnum(str, Enum):
    ECLIPTIC_TRUE_OF_DATE = "ecliptic_true_of_date"
    ICRS_J2000 = "icrs_j2000"


class ZodiacMode(str, Enum):
    TROPICAL = "tropical"
    SIDEREAL = "sidereal"


@dataclass
class BodyPosition:
    frame: str
    mode: str  # geocentric / topocentric
    zodiac: ZodiacMode
    lon_deg: float
    lat_deg: float
    dist_au: Optional[float] = None
    speed_lon_deg_per_day: Optional[float] = None
    flags: Optional[dict[str, bool]] = None
    quality: Optional[dict[str, Any]] = None


# -----------------------------------------------------------------------------
# Western: houses, angles, aspects, placements
# -----------------------------------------------------------------------------


@dataclass
class WesternHouses:
    system: Optional[str] = None  # P,K,R,C,E,W,O,S
    cusps_deg: Optional[Sequence[float]] = None  # 12 cusps
    angles_asc_deg: Optional[float] = None
    angles_mc_deg: Optional[float] = None
    status: Optional[BlockStatus] = None


@dataclass
class AspectEntry:
    a: str
    b: str
    type: str
    exact_angle_deg: float
    orb_deg: float
    applying: bool


@dataclass
class PlacementEntry:
    sign: str
    degree_in_sign: float
    house: Optional[int] = None
    retrograde: bool = False


# -----------------------------------------------------------------------------
# Vedic
# -----------------------------------------------------------------------------


@dataclass
class VedicAyanamsha:
    mode: str  # SE sidereal mode
    nutation_included: Optional[bool] = None


@dataclass
class PanchangaBlock:
    vaara: Optional[str] = None
    tithi_index: Optional[int] = None  # 1-30
    tithi_ends_at_local: Optional[str] = None
    nakshatra_index: Optional[int] = None  # 1-27
    yoga_index: Optional[int] = None     # 1-27
    karana_indices: Optional[Sequence[int]] = None  # 1-60
    sunrise_method: Optional[str] = None  # astronomical_upper_limb / hindu_rising
    status: Optional[BlockStatus] = None


# -----------------------------------------------------------------------------
# Chinese
# -----------------------------------------------------------------------------


class YearBoundary(str, Enum):
    LICHUN = "lichun"
    CNY_LUNISOLAR = "cny_lunisolar"


@dataclass
class GanzhiDay:
    stem: str   # 10 stems
    branch: str # 12 branches
    index_60: int  # 1-60


@dataclass
class BaziPillar:
    stem: str
    branch: str


@dataclass
class ChineseBlock:
    boundary_year: Optional[str] = None  # lichun / cny_lunisolar
    solar_terms: Optional[dict[str, Optional[str]]] = None  # J1..Z12 -> ISO-8601
    ganzhi_day: Optional[GanzhiDay] = None
    bazi_pillars: Optional[dict[str, Optional[BaziPillar]]] = None  # year, month, day, hour
    calendar_day_definition: Optional[str] = None  # utc+8
    status: Optional[BlockStatus] = None


# -----------------------------------------------------------------------------
# Meta / engine
# -----------------------------------------------------------------------------


@dataclass
class EngineMeta:
    ephemeris_engine: str
    house_engine: str
    tz_engine: str
    code_hash: Optional[str] = None
    license_mode: Optional[str] = None


@dataclass
class HoroscoopMeta:
    version: str  # semver
    generated_at_utc: str  # ISO-8601
    engine: EngineMeta


# -----------------------------------------------------------------------------
# Top-level horoscoop output
# -----------------------------------------------------------------------------


@dataclass
class HoroscoopOutput:
    meta: HoroscoopMeta
    input: dict[str, Any]  # birth date, time, place, timezone
    time: TimeBlock
    astronomy: dict[str, Any]  # bodies.{id}: BodyPosition-like dict
    western: Optional[dict[str, Any]] = None  # houses, aspects, placements
    vedic: Optional[dict[str, Any]] = None
    chinese: Optional[dict[str, Any]] = None
    diagnostics: Optional[dict[str, Any]] = None
