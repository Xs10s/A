"""
Jyotish-style sidereal rashi chart helpers (whole-sign bhava from sidereal Lagna).

Uses tropical ecliptic longitudes plus ayanamsha to sidereal (nirayana).
House system: whole sign from sidereal ascendant (explicitly not equal-area, not Placidus).

This module is intentionally separate from western placements-aspect logic.
"""
from __future__ import annotations

from typing import Any, Optional

from . import sidereal
from . import vedic

SIGN_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Traditional sign lords (Parashari-style; no outer planets).
SIGN_LORD_EN: dict[int, str] = {
    0: "Mars",
    1: "Venus",
    2: "Mercury",
    3: "Moon",
    4: "Sun",
    5: "Mercury",
    6: "Venus",
    7: "Mars",
    8: "Jupiter",
    9: "Saturn",
    10: "Saturn",
    11: "Jupiter",
}

# Vimshottari nakshatra rulers (27), index 1 = Ashwini
_NAKSHATRA_LORDS: tuple[str, ...] = tuple(
    ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"] * 3
)


def nakshatra_lord_en(nak_index_1_27: int) -> str:
    idx = int(nak_index_1_27)
    if idx < 1 or idx > 27:
        return ""
    return _NAKSHATRA_LORDS[idx - 1]

# Vaara index 0=Sunday through 6=Saturday; maps to day lord (Hindu / Jyotish convention).
VAARA_DAY_LORD: dict[int, str] = {
    0: "Sun",
    1: "Moon",
    2: "Mars",
    3: "Mercury",
    4: "Jupiter",
    5: "Venus",
    6: "Saturn",
}

CHARA_RASHIS = {0, 3, 6, 9}   # movable
STHIRA_RASHIS = {1, 4, 7, 10}  # fixed
DWISVA_RASHIS = {2, 5, 8, 11}  # dual

TATTVA_BY_SIGN = {
    0: "fire", 4: "fire", 8: "fire",
    1: "earth", 5: "earth", 9: "earth",
    2: "air", 6: "air", 10: "air",
    3: "water", 7: "water", 11: "water",
}

# Simple three-guna association by sign element / modality heuristics used for UI summary only.
GUNA_BY_SIGN = {
    0: "rajas", 4: "sattva", 8: "sattva",
    1: "tamas", 5: "rajas", 9: "tamas",
    2: "rajas", 6: "sattva", 10: "sattva",
    3: "tamas", 7: "tamas", 11: "sattva",
}


def _degree_in_sign(sid_lon: float) -> float:
    return sid_lon % 30.0


def _rashi_index(sid_lon: float) -> int:
    return int((sid_lon % 360.0) // 30) % 12


def nakshatra_pada_from_longitude_deg(sid_lon: float) -> tuple[int, int]:
    """Return (nakshatra_index 1..27, pada 1..4)."""
    lon = sid_lon % 360.0
    nwid = vedic.NAKSHATRA_WIDTH_DEG
    n_idx = 1 + int(lon / nwid) % 27
    pos_in_n = lon - (n_idx - 1) * nwid
    pada = int(pos_in_n / (nwid / 4.0)) + 1
    if pada > 4:
        pada = 4
    return n_idx, pada


def navamsa_rashi_index(sid_lon: float) -> int:
    """Navamsha sign index 0..11 from sidereal longitude."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = int(d / (30.0 / 9.0))  # 0..8
    if r0 in (0, 4, 8):
        start = 0
    elif r0 in (1, 5, 9):
        start = 9
    elif r0 in (2, 6, 10):
        start = 6
    else:
        start = 3
    return (start + seg) % 12


def dashamsa_rashi_index(sid_lon: float) -> int:
    """Dashamsha (D10) sign index 0..11."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = int(d / 3.0)  # 0..9
    r1 = r0 + 1  # 1-based sign position
    if r1 % 2 == 1:
        start = r0
    else:
        start = (r0 + 8) % 12
    return (start + seg) % 12


def hora_rashi_index(sid_lon: float) -> int:
    """D2 Hora: Parashara solar/lunar halves per odd and even signs."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    first_half = d < 15.0
    odd = r0 % 2 == 0  # Mesha (0) odd sign in 0-based parity used elsewhere in this module
    if odd:
        return 4 if first_half else 3  # Leo / Cancer
    return 3 if first_half else 4


def drekkana_rashi_index(sid_lon: float) -> int:
    """D3 Drekkana: same sign, fifth, ninth for three ten-degree parts."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = min(int(d / 10.0), 2)
    return (r0 + seg * 4) % 12


def chaturthamsa_rashi_index(sid_lon: float) -> int:
    """D4 Chaturthamsa: four 7.5-degree parts; movable, fixed, dual rules."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    q = min(int(d / 7.5), 3)
    if r0 in CHARA_RASHIS:
        return (r0 + q * 3) % 12
    if r0 in STHIRA_RASHIS:
        return (r0 + 9 + q * 3) % 12
    return (r0 + 6 + q * 3) % 12


def saptamsa_rashi_index(sid_lon: float) -> int:
    """D7 Saptamsa: seven parts; odd signs from same sign, even signs from 7th."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = min(int(d / (30.0 / 7.0)), 6)
    base = r0 if r0 % 2 == 0 else (r0 + 6) % 12
    return (base + seg) % 12


def dwadasamsa_rashi_index(sid_lon: float) -> int:
    """D12 Dwadasamsa: twelve 2.5-degree steps from the sign."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = min(int(d / 2.5), 11)
    return (r0 + seg) % 12


def shodasamsa_rashi_index(sid_lon: float) -> int:
    """D16 Shodasamsa: movable from Aries, fixed from Leo, dual from Sagittarius."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = min(int(d / (30.0 / 16.0)), 15)
    if r0 in CHARA_RASHIS:
        base = 0
    elif r0 in STHIRA_RASHIS:
        base = 4
    else:
        base = 8
    return (base + seg) % 12


def vimshamsa_rashi_index(sid_lon: float) -> int:
    """D20 Vimshamsa: movable from Aries, fixed from Sagittarius, dual from Leo."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = min(int(d / 1.5), 19)
    if r0 in CHARA_RASHIS:
        base = 0
    elif r0 in STHIRA_RASHIS:
        base = 8
    else:
        base = 4
    return (base + seg) % 12


def siddhamsa_rashi_index(sid_lon: float) -> int:
    """D24 Chaturvimshamsa / Siddhamsa: odd signs from Leo, even signs from Cancer."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = min(int(d / 1.25), 23)
    base = 4 if r0 % 2 == 0 else 3
    return (base + seg) % 12


def nakshatramsha_rashi_index(sid_lon: float) -> int:
    """D27 Nakshatramsha: by triplicity (fire/earth/air/water) starting sign."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = min(int(d / (30.0 / 27.0)), 26)
    if r0 in (0, 4, 8):
        base = 0
    elif r0 in (1, 5, 9):
        base = 3
    elif r0 in (2, 6, 10):
        base = 6
    else:
        base = 9
    return (base + seg) % 12


def trimshamsa_rashi_index(sid_lon: float) -> int:
    """D30 Trimshamsa: unequal portions; even signs reverse ruler order."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    odd = r0 % 2 == 0
    # (cumulative_deg_end, sign_index) Parashari mapping
    odd_bounds: tuple[tuple[float, int], ...] = ((5.0, 8), (12.0, 10), (20.0, 9), (27.0, 2), (30.0, 6))
    even_bounds: tuple[tuple[float, int], ...] = ((5.0, 6), (12.0, 2), (20.0, 9), (27.0, 10), (30.0, 8))
    for end, six in (odd_bounds if odd else even_bounds):
        if d < end:
            return six
    return (odd_bounds if odd else even_bounds)[-1][1]


def khavedamsa_rashi_index(sid_lon: float) -> int:
    """D40 Khavedamsa: odd signs from Aries, even signs from Libra."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = min(int(d / 0.75), 39)
    base = 0 if r0 % 2 == 0 else 6
    return (base + seg) % 12


def akshavedamsa_rashi_index(sid_lon: float) -> int:
    """D45 Akshavedamsa: same triplicity starts as D16."""
    return shodasamsa_rashi_index(sid_lon)


def shashtiamsa_rashi_index(sid_lon: float) -> int:
    """D60 Shashtiamsa: sixty half-degree steps from the sign."""
    r0 = _rashi_index(sid_lon)
    d = _degree_in_sign(sid_lon)
    seg = min(int(d / 0.5), 59)
    return (r0 + seg) % 12


_VARGA_RASHI_INDEX_FN: dict[str, Any] = {
    "D1": _rashi_index,
    "D2": hora_rashi_index,
    "D3": drekkana_rashi_index,
    "D4": chaturthamsa_rashi_index,
    "D7": saptamsa_rashi_index,
    "D9": navamsa_rashi_index,
    "D10": dashamsa_rashi_index,
    "D12": dwadasamsa_rashi_index,
    "D16": shodasamsa_rashi_index,
    "D20": vimshamsa_rashi_index,
    "D24": siddhamsa_rashi_index,
    "D27": nakshatramsha_rashi_index,
    "D30": trimshamsa_rashi_index,
    "D40": khavedamsa_rashi_index,
    "D45": akshavedamsa_rashi_index,
    "D60": shashtiamsa_rashi_index,
}

SHODASHA_VARGA_IDS: tuple[str, ...] = tuple(_VARGA_RASHI_INDEX_FN.keys())


def varga_rashi_index(varga_id: str, sid_lon: float) -> int:
    fn = _VARGA_RASHI_INDEX_FN.get(str(varga_id))
    if fn is None:
        return _rashi_index(sid_lon)
    return int(fn(sid_lon))


def build_varga_map(sid_lon: float, lagna_sid: Optional[float]) -> dict[str, dict[str, Any]]:
    """Per-varga rashi + whole-sign house from varga-Lagna, for one longitude."""
    out: dict[str, dict[str, Any]] = {}
    for vid in SHODASHA_VARGA_IDS:
        fn = _VARGA_RASHI_INDEX_FN[vid]
        ri = int(fn(sid_lon))
        house: Optional[int] = None
        if lagna_sid is not None:
            lr = int(fn(lagna_sid))
            house = int(whole_sign_house_from_reference_sign(ri, lr))
        out[vid] = {
            "rashi_index": ri,
            "rashi": SIGN_NAMES_EN[ri],
            "house": house,
        }
    return out


def whole_sign_house_from_reference_sign(body_sign_idx: int, ref_sign_idx: int) -> int:
    """Bhava 1..12 when ref_sign_idx is 'lagna' sign index 0..11 for the divisional chart."""
    return (body_sign_idx - ref_sign_idx + 12) % 12 + 1


def whole_sign_house_from_lagnah(sid_body: float, sid_lagna: float) -> int:
    """Bhava 1..12: sign distance from Lagna sign + 1."""
    rb = _rashi_index(sid_body)
    rl = _rashi_index(sid_lagna)
    return whole_sign_house_from_reference_sign(rb, rl)


def _kendra_houses_from(house1: int) -> set[int]:
    """Kendra (1,4,7,10) counted from house1 as temporary 'lagna' house."""
    h = house1
    return {h, (h + 3 - 1) % 12 + 1, (h + 6 - 1) % 12 + 1, (h + 9 - 1) % 12 + 1}


def _trikona_from_lagna(lagna_house: int) -> set[int]:
    return {lagna_house, (lagna_house + 4 + 11) % 12 + 1, (lagna_house + 8 + 11) % 12 + 1}


def house_kind_for_planet(house: int, lagna_house: int) -> str:
    """Functional house class label for UI (1-based houses)."""
    k = _kendra_houses_from(lagna_house)
    t = _trikona_from_lagna(lagna_house)
    if house in k:
        return "kendra"
    if house in t:
        return "trikona"
    if house in (6, 8, 12):
        return "dusthana"
    return "other"


def bhava_groups_for_house(house: int) -> list[str]:
    """
    Static whole-sign bhava group tags (1..12), not counted from a movable reference.
    Dharma/Artha/Kama/Moksha triplicity; kendra; trikona (same triad as dharma); dusthana; upachaya.
    """
    h = int(house)
    tags: list[str] = []
    if h in (1, 4, 7, 10):
        tags.append("kendra")
    if h in (1, 5, 9):
        tags.append("trikona")
    if h in (1, 5, 9):
        tags.append("dharma")
    if h in (2, 6, 10):
        tags.append("artha")
    if h in (3, 7, 11):
        tags.append("kama")
    if h in (4, 8, 12):
        tags.append("moksha")
    if h in (6, 8, 12):
        tags.append("dusthana")
    if h in (3, 6, 10, 11):
        tags.append("upachaya")
    return tags


def rashi_polarity(sign_ix: int) -> str:
    """Sign gender for rashi (Mesha purusha, Vrishabha stri, ...)."""
    return "purusha" if int(sign_ix) % 2 == 0 else "stri"


# Exaltation / debilitation rashi indices (0=Aries through 11=Pisces), classical seven only.
_EXALT_RASHI: dict[str, int] = {
    "Sun": 0,
    "Moon": 1,
    "Mars": 9,
    "Mercury": 5,
    "Jupiter": 3,
    "Venus": 11,
    "Saturn": 6,
}
_DEBIL_RASHI: dict[str, int] = {
    "Sun": 6,
    "Moon": 7,
    "Mars": 3,
    "Mercury": 11,
    "Jupiter": 9,
    "Venus": 5,
    "Saturn": 0,
}
_OWN_RASHIS: dict[str, set[int]] = {
    "Sun": {4},
    "Moon": {3},
    "Mars": {0, 7},
    "Mercury": {2, 5},
    "Jupiter": {8, 11},
    "Venus": {1, 6},
    "Saturn": {9, 10},
}
_MULA_RASHI: dict[str, int] = {
    "Sun": 4,
    "Moon": 1,
    "Mars": 0,
    "Mercury": 5,
    "Jupiter": 8,
    "Venus": 6,
    "Saturn": 10,
}

# Par??ari-style permanent friendship (naisargika): relation of FROM graha toward TO graha.
_NAISARGIKA: dict[str, dict[str, frozenset[str]]] = {
    "Sun": {
        "friend": frozenset({"Moon", "Mars", "Jupiter"}),
        "neutral": frozenset({"Mercury"}),
        "enemy": frozenset({"Venus", "Saturn"}),
    },
    "Moon": {
        "friend": frozenset({"Sun", "Mercury"}),
        "neutral": frozenset({"Mars", "Jupiter", "Venus", "Saturn"}),
        "enemy": frozenset(),
    },
    "Mars": {
        "friend": frozenset({"Sun", "Moon", "Jupiter"}),
        "neutral": frozenset({"Venus", "Saturn"}),
        "enemy": frozenset({"Mercury"}),
    },
    "Mercury": {
        "friend": frozenset({"Sun", "Venus"}),
        "neutral": frozenset({"Mars", "Jupiter", "Saturn"}),
        "enemy": frozenset({"Moon"}),
    },
    "Jupiter": {
        "friend": frozenset({"Sun", "Moon", "Mars"}),
        "neutral": frozenset({"Mercury", "Saturn"}),
        "enemy": frozenset({"Venus"}),
    },
    "Venus": {
        "friend": frozenset({"Mercury", "Saturn"}),
        "neutral": frozenset({"Mars", "Jupiter"}),
        "enemy": frozenset({"Sun", "Moon"}),
    },
    "Saturn": {
        "friend": frozenset({"Mercury", "Venus"}),
        "neutral": frozenset({"Jupiter"}),
        "enemy": frozenset({"Sun", "Moon", "Mars"}),
    },
}


def _naisargika_bandhu(from_en: str, toward_en: str) -> Optional[str]:
    """Return 'friend', 'neutral', or 'enemy' of from_en toward toward_en; None if unknown."""
    if from_en == toward_en:
        return None
    row = _NAISARGIKA.get(from_en)
    if not row:
        return None
    if toward_en in row["friend"]:
        return "friend"
    if toward_en in row["enemy"]:
        return "enemy"
    if toward_en in row["neutral"]:
        return "neutral"
    return "neutral"


def natural_dignity(name_en: str, rashi_index: int) -> Optional[dict[str, Any]]:
    """Natural (naisargika) dignity: uchcha/neecha/own/mula, else mitra/sama/satru to sign lord."""
    ri = int(rashi_index) % 12
    lord = SIGN_LORD_EN[ri]

    if name_en in ("Rahu", "Ketu"):
        return {
            "code": "nodes",
            "label_nl": "Rahu/Ketu: geen uchcha/neecha in klassieke zevenfold",
            "label_en": "Rahu/Ketu: no classical exaltation/debilitation",
            "rashilord_en": lord,
        }
    if name_en not in _EXALT_RASHI:
        return None
    if ri == _EXALT_RASHI[name_en]:
        return {"code": "exalted", "label_nl": "Uccha (verheven)", "label_en": "Uccha (exalted)", "rashilord_en": lord}
    if ri == _DEBIL_RASHI[name_en]:
        return {"code": "debilitated", "label_nl": "Nicha (gedebiliteerd)", "label_en": "Nicha (debilitated)", "rashilord_en": lord}
    if ri in _OWN_RASHIS.get(name_en, set()):
        return {"code": "own", "label_nl": "Swa-rashi (eigen teken)", "label_en": "Sva-rashi (own sign)", "rashilord_en": lord}
    if ri == _MULA_RASHI.get(name_en):
        return {"code": "mulatrikona", "label_nl": "Mulatrikona", "label_en": "Mulatrikona", "rashilord_en": lord}

    rel = _naisargika_bandhu(name_en, lord)
    if rel == "friend":
        return {
            "code": "mitra_sign_lord",
            "label_nl": f"Mitra (vriend) tot tekeneheer {lord}",
            "label_en": f"Mitra (friend) toward sign lord {lord}",
            "rashilord_en": lord,
        }
    if rel == "enemy":
        return {
            "code": "satru_sign_lord",
            "label_nl": f"Satru (vijand) tot tekeneheer {lord}",
            "label_en": f"Satru (enemy) toward sign lord {lord}",
            "rashilord_en": lord,
        }
    return {
        "code": "sama_sign_lord",
        "label_nl": f"Sama (neutraal) tot tekeneheer {lord}",
        "label_en": f"Sama (neutral) toward sign lord {lord}",
        "rashilord_en": lord,
    }


def _aspect_targets_whole_sign(house_of_graha: int, graha_en: str) -> list[int]:
    """
    Graha drishti on whole-sign houses (counting from occupied bhava).

    All classical grahas aspect the 7th from their house.
    Mars: 4,7,8; Jupiter: 5,7,9; Saturn: 3,7,10.
    """
    h = house_of_graha
    bases = [(h + 6 - 1) % 12 + 1]  # 7th (Jaimini style: same as 180- sign)
    extra: list[int] = []
    if graha_en == "Mars":
        extra = [(h + 3 - 1) % 12 + 1, (h + 6 - 1) % 12 + 1, (h + 7 - 1) % 12 + 1]
    elif graha_en == "Jupiter":
        extra = [(h + 4 - 1) % 12 + 1, (h + 6 - 1) % 12 + 1, (h + 8 - 1) % 12 + 1]
    elif graha_en == "Saturn":
        extra = [(h + 2 - 1) % 12 + 1, (h + 6 - 1) % 12 + 1, (h + 9 - 1) % 12 + 1]
    elif graha_en in ("Rahu", "Ketu"):
        return []  # conscious omission unless separate tradition flag exists
    merged = bases + [x for x in extra if x not in bases]
    return sorted(set(merged))


def _detect_yogas(grahas: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Only yogas we can state from house geometry without speculative text factories.
    """
    moon = grahas.get("Moon") or {}
    jup = grahas.get("Jupiter") or {}
    mh = moon.get("house")
    jh = jup.get("house")
    out: list[dict[str, Any]] = []
    if mh is not None and jh is not None:
        k_from_moon = _kendra_houses_from(int(mh))
        if int(jh) in k_from_moon:
            out.append({
                "id": "gaja_kesari",
                "name_nl": "Gaja Kesari-yoga",
                "name_en": "Gaja Kesari yoga",
                "reason_nl": "Jupiter staat in kendra vanaf de Maan (1/4/7/10 vanaf het Maan-huis).",
                "reason_en": "Jupiter occupies a kendra counted from the Moon (1/4/7/10 from the Moon house).",
                "bodies": ["Moon", "Jupiter"],
            })
    # No additional yogas without exact rule checks.
    ak = None
    for g in grahas.values():
        if isinstance(g, dict) and g.get("is_atmakaraka_candidate"):
            ak = g.get("name_en")
            break
    if ak:
        ak_h = (grahas.get(ak) or {}).get("house")
        if ak_h is not None and int(ak_h) in (1, 4, 7, 10):
            out.append({
                "id": "atmakaraka_kendra",
                "name_nl": "Atmakaraka in kendra",
                "name_en": "Atmakaraka in angular house",
                "reason_nl": f"Atmakaraka ({ak}) staat in huis {ak_h} (kendra vanaf Lagna).",
                "reason_en": f"Atmakaraka ({ak}) falls in house {ak_h} (kendra from Lagna).",
                "bodies": [ak],
            })
    return out


def build_jyotish_chart(
    *,
    jd_tt: float,
    western_block: Optional[dict[str, Any]],
    astronomy_block: dict[str, Any],
    ayanamsha_mode: str,
    vaara_index: Optional[int],
    birth_time_reliable: bool,
) -> dict[str, Any]:
    """
    Returns a JSON-safe dict under vedic.jyotish.

    If no western ascendant: still returns sidereal longitudes & rashis where possible,
    but houses are null.
    """
    sid_mode = sidereal.AYANAMSHA_MODES.get(ayanamsha_mode, sidereal.SE_SIDM_LAHIRI)
    aya_deg, nut, _err = sidereal.ayanamsha_with_nutation(jd_tt, sid_mode)

    bodies = (astronomy_block or {}).get("bodies") or {}

    def trop_lon(name: str) -> Optional[float]:
        bb = bodies.get(name)
        if not isinstance(bb, dict) or bb.get("lon_deg") is None:
            return None
        return float(bb["lon_deg"])

    def retro_of(name: str) -> Optional[bool]:
        bb = bodies.get(name)
        if not isinstance(bb, dict):
            return None
        spd = bb.get("speed_lon_deg_per_day")
        if spd is None:
            return None
        return bool(float(spd) < 0)

    asc_tropical: Optional[float] = None
    if western_block:
        asc_tropical = (((western_block.get("houses") or {}).get("angles") or {}).get("asc_deg"))
        if asc_tropical is not None:
            asc_tropical = float(asc_tropical)

    lagna_sid: Optional[float] = None
    if asc_tropical is not None:
        lagna_sid = sidereal.tropical_to_sidereal_deg(asc_tropical, aya_deg)

    classical = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    sid_by_name: dict[str, float] = {}
    for name in classical:
        lon_t = trop_lon(name)
        if lon_t is None:
            continue
        sid_by_name[name] = sidereal.tropical_to_sidereal_deg(lon_t, aya_deg)

    graha_rows: list[dict[str, Any]] = []
    for name in classical:
        sid = sid_by_name.get(name)
        if sid is None:
            continue
        rashi = SIGN_NAMES_EN[_rashi_index(sid)]
        nak, pada = nakshatra_pada_from_longitude_deg(sid)
        nk_lord = nakshatra_lord_en(nak)
        house = int(whole_sign_house_from_lagnah(sid, lagna_sid)) if lagna_sid is not None else None
        deg_in = round(_degree_in_sign(sid), 4)
        ri = _rashi_index(sid)
        nav_ix = navamsa_rashi_index(sid)
        d10_ix = dashamsa_rashi_index(sid)
        graha_rows.append({
            "name_en": name,
            "sidereal_lon_deg": round(sid, 5),
            "degree_in_sign": deg_in,
            "rashi": rashi,
            "rashi_index": ri,
            "nakshatra_index": nak,
            "nakshatra_lord_en": nk_lord,
            "pada": pada,
            "navamsa_rashi": SIGN_NAMES_EN[nav_ix],
            "navamsa_rashi_index": nav_ix,
            "dashamsa_rashi": SIGN_NAMES_EN[d10_ix],
            "dashamsa_rashi_index": d10_ix,
            "house": house,
            "retrograde": retro_of(name),
            "tattva": TATTVA_BY_SIGN.get(ri),
            "guna_summary": GUNA_BY_SIGN.get(ri),
            "sign_quality": "chara" if ri in CHARA_RASHIS else ("sthira" if ri in STHIRA_RASHIS else "dwisvabhava"),
            "house_kind_from_lagna": house_kind_for_planet(house, 1) if house is not None else None,
            "combust": _is_combust(name, sid, sid_by_name.get("Sun")),
            "vargas": build_varga_map(sid, lagna_sid),
        })

    rahu_t = trop_lon("NorthNode")
    if rahu_t is not None:
        sid_r = sidereal.tropical_to_sidereal_deg(rahu_t, aya_deg)
        sid_k = (sid_r + 180.0) % 360.0
        for label, sid in (("Rahu", sid_r), ("Ketu", sid_k)):
            ri = _rashi_index(sid)
            nak, pada = nakshatra_pada_from_longitude_deg(sid)
            nk_lord = nakshatra_lord_en(nak)
            house = int(whole_sign_house_from_lagnah(sid, lagna_sid)) if lagna_sid is not None else None
            nv = navamsa_rashi_index(sid)
            d10 = dashamsa_rashi_index(sid)
            graha_rows.append({
                "name_en": label,
                "sidereal_lon_deg": round(sid, 5),
                "degree_in_sign": round(_degree_in_sign(sid), 4),
                "rashi": SIGN_NAMES_EN[ri],
                "rashi_index": ri,
                "nakshatra_index": nak,
                "nakshatra_lord_en": nk_lord,
                "pada": pada,
                "navamsa_rashi": SIGN_NAMES_EN[nv],
                "navamsa_rashi_index": nv,
                "dashamsa_rashi": SIGN_NAMES_EN[d10],
                "dashamsa_rashi_index": d10,
                "house": house,
                "retrograde": True,  # nodes conventionally retrograde in many tables
                "tattva": TATTVA_BY_SIGN.get(ri),
                "guna_summary": GUNA_BY_SIGN.get(ri),
                "sign_quality": "chara" if ri in CHARA_RASHIS else ("sthira" if ri in STHIRA_RASHIS else "dwisvabhava"),
                "house_kind_from_lagna": house_kind_for_planet(house, 1) if house is not None else None,
                "combust": False,
                "vargas": build_varga_map(sid, lagna_sid),
            })
            sid_by_name[label] = sid

    # Atmakaraka among classical seven by highest degree_in_sign (ties: standard weekday order not needed if unique deg)
    ak_name: Optional[str] = None
    candidates = [g for g in graha_rows if g["name_en"] in classical and g.get("degree_in_sign") is not None]
    if candidates:
        candidates.sort(key=lambda g: float(g["degree_in_sign"]), reverse=True)
        ak_name = str(candidates[0]["name_en"])
    for g in graha_rows:
        g["is_atmakaraka_candidate"] = (g.get("name_en") == ak_name and g["name_en"] in classical)

    lagna_house_for_kind = 1
    for g in graha_rows:
        ri = g.get("rashi_index")
        if isinstance(ri, int):
            nd = natural_dignity(str(g["name_en"]), int(ri))
            if nd is not None:
                g["natural_dignity"] = nd
        h = g.get("house")
        if h is not None:
            g["bhava_groups"] = bhava_groups_for_house(int(h))
            g["house_kind_from_lagna"] = house_kind_for_planet(int(h), lagna_house_for_kind)

    grahas_by = {g["name_en"]: g for g in graha_rows}
    yogas = _detect_yogas(grahas_by)

    lagna_nav_ix: Optional[int] = None
    lagna_d10_ix: Optional[int] = None
    if lagna_sid is not None:
        lagna_nav_ix = navamsa_rashi_index(lagna_sid)
        lagna_d10_ix = dashamsa_rashi_index(lagna_sid)
        for g in graha_rows:
            nv = g.get("navamsa_rashi_index")
            d0 = g.get("dashamsa_rashi_index")
            if isinstance(nv, int) and lagna_nav_ix is not None:
                g["navamsa_house"] = whole_sign_house_from_reference_sign(int(nv), int(lagna_nav_ix))
            if isinstance(d0, int) and lagna_d10_ix is not None:
                g["dashamsa_house"] = whole_sign_house_from_reference_sign(int(d0), int(lagna_d10_ix))

    lagna_info: Optional[dict[str, Any]] = None
    lagnesha: Optional[dict[str, Any]] = None
    if lagna_sid is not None:
        lr = _rashi_index(lagna_sid)
        lord = SIGN_LORD_EN[lr]
        lord_row = next((x for x in graha_rows if x["name_en"] == lord), None)
        ln_idx, ln_pada = nakshatra_pada_from_longitude_deg(lagna_sid)
        lagna_info = {
            "sidereal_deg": round(lagna_sid, 5),
            "rashi": SIGN_NAMES_EN[lr],
            "rashi_index": lr,
            "nakshatra_index": ln_idx,
            "nakshatra_lord_en": nakshatra_lord_en(ln_idx),
            "pada": ln_pada,
            "navamsa_rashi": SIGN_NAMES_EN[int(lagna_nav_ix)] if lagna_nav_ix is not None else None,
            "navamsa_rashi_index": int(lagna_nav_ix) if lagna_nav_ix is not None else None,
            "dashamsa_rashi": SIGN_NAMES_EN[int(lagna_d10_ix)] if lagna_d10_ix is not None else None,
            "dashamsa_rashi_index": int(lagna_d10_ix) if lagna_d10_ix is not None else None,
            "vargas": {
                vid: {
                    "rashi_index": int(v["rashi_index"]),
                    "rashi": str(v["rashi"]),
                    "house": 1,
                }
                for vid, v in build_varga_map(lagna_sid, lagna_sid).items()
            },
        }
        if lord_row:
            lrashi = lord_row.get("rashi")
            lhouse = lord_row.get("house")
            lhouse_kind = lord_row.get("house_kind_from_lagna")
            lagnesha = {
                "lord": lord,
                "in_rashi": lrashi,
                "in_house": lhouse,
                "house_kind_from_lagna": lhouse_kind,
                "degree_in_sign": lord_row.get("degree_in_sign"),
            }

    drishti_out: list[dict[str, Any]] = []
    for g in graha_rows:
        h = g.get("house")
        name = str(g["name_en"])
        if h is None:
            continue
        targets = _aspect_targets_whole_sign(int(h), name)
        if not targets:
            continue
        drishti_out.append({"from": name, "from_house": int(h), "houses": targets})

    d1_bhavas: list[dict[str, Any]] = []
    if lagna_sid is not None:
        lag_ix = _rashi_index(lagna_sid)
        for bh in range(1, 13):
            sign_ix = (lag_ix + bh - 1) % 12
            sq = "chara" if sign_ix in CHARA_RASHIS else ("sthira" if sign_ix in STHIRA_RASHIS else "dwisvabhava")
            d1_bhavas.append({
                "house": bh,
                "rashi_index": sign_ix,
                "rashi": SIGN_NAMES_EN[sign_ix],
                "lord_en": SIGN_LORD_EN[sign_ix],
                "bhava_groups": bhava_groups_for_house(bh),
                "tattva": TATTVA_BY_SIGN.get(sign_ix),
                "sign_quality": sq,
                "polarity": rashi_polarity(sign_ix),
            })

    # Panchanga Vaara day lord (separate from chart; reported for UI)
    day_lord_en = VAARA_DAY_LORD.get(int(vaara_index), None) if vaara_index is not None else None

    # Aggregation for energy strip
    tattva_counts: dict[str, int] = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    guna_counts: dict[str, int] = {"sattva": 0, "rajas": 0, "tamas": 0}
    qual_counts: dict[str, int] = {"chara": 0, "sthira": 0, "dwisvabhava": 0}
    for g in graha_rows:
        if str(g["name_en"]) in ("Rahu", "Ketu"):
            continue
        tt = g.get("tattva")
        if tt in tattva_counts:
            tattva_counts[tt] += 1
        gn = g.get("guna_summary")
        if gn in guna_counts:
            guna_counts[gn] += 1
        sq = g.get("sign_quality")
        if sq in qual_counts:
            qual_counts[sq] += 1

    out: dict[str, Any] = {
        "status": {
            "computed": bool(graha_rows),
            "house_model": "whole_sign_from_sidereal_lagna",
            "requires": ["date", "time", "location", "timezone"],
            "confidence": "high" if birth_time_reliable and lagna_sid is not None else "medium",
            "warnings": [],
            "assumptions": [
                "Huizen volgens whole sign vanaf sidereale Lagna (Lahiri of gekozen ayanamsha).",
                "Geen Westerse aspectorbits of Placidus-huizen hergebruikt voor deze laag.",
            ],
        },
        "ayanamsha": {"mode": ayanamsha_mode, "deg": round(float(aya_deg), 6), "nutation_included": nut},
        "lagna": lagna_info,
        "lagnesha": lagnesha,
        "grahas": graha_rows,
        "d1_bhavas": d1_bhavas,
        "drishti": drishti_out,
        "yogas": yogas,
        "vaara_day_lord_en": day_lord_en,
        "atmakaraka_en": ak_name,
        "tattva_counts": tattva_counts,
        "guna_counts": guna_counts,
        "rashi_quality_counts": qual_counts,
        "vimshottari": {
            "available": False,
            "note_nl": "Vimshottari Mahadasha/Antardasha wordt later gekoppeld aan betrouwbare Maan-Nakshatra-timing; hier nog geen volledige periodelijst.",
            "note_en": "Vimshottari Mahadasha/Antardasha will be wired to reliable Moon-nakshatra timing later; no full period table yet.",
        },
    }
    if not birth_time_reliable:
        out["status"]["warnings"].append("BIRTH_TIME_UNCERTAIN")
    if lagna_sid is None:
        out["status"]["warnings"].append("NO_LAGNA")
        out["status"]["confidence"] = "low"

    _div_labels = {
        "D1": "Rashi",
        "D2": "Hora",
        "D3": "Drekkana",
        "D4": "Chaturthamsa",
        "D7": "Saptamsa",
        "D9": "Navamsa",
        "D10": "Dashamsa",
        "D12": "Dwadasamsa",
        "D16": "Shodasamsa",
        "D20": "Vimshamsa",
        "D24": "Chaturvimshamsa",
        "D27": "Nakshatramsha",
        "D30": "Trimshamsa",
        "D40": "Khavedamsa",
        "D45": "Akshavedamsa",
        "D60": "Shashtiamsa",
    }
    out["divisional_charts"] = {
        vid: {
            "label": _div_labels.get(vid, vid),
            "available": True,
            **(
                {
                    "note_nl": "D60 is subtiel; bij onzekere geboortetijd voorzichtig lezen.",
                    "note_en": "D60 is subtle; read cautiously if birth time is uncertain.",
                }
                if vid == "D60" and not birth_time_reliable
                else {}
            ),
        }
        for vid in SHODASHA_VARGA_IDS
    }

    return out


def _is_combust(name: str, sid_body: float, sid_sun: Optional[float]) -> bool:
    if name == "Sun" or sid_sun is None:
        return False
    if name not in ("Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        return False
    if _rashi_index(sid_body) != _rashi_index(sid_sun):
        return False
    diff = abs((sid_body - sid_sun + 180.0) % 360.0 - 180.0)
    # Approximate standard combustion orbs vary; use conservative 8- for Mercury/Venus, 10- Moon, 12- others.
    orb = 12.0
    if name == "Moon":
        orb = 12.0
    elif name in ("Venus", "Mercury"):
        orb = 10.0
    return diff < orb and diff > 1e-6
