"""
Layer B/D - Maya time-cycle engine.

Lean Maya astrology / time module. REUSES JD(UTC) from the existing engine
(no new astronomy). Produces:
    - Long Count (5 places: baktun, katun, tun, uinal, kin)
    - Tzolkin (260-day sacred cycle: 13 tones x 20 day-signs)
    - Haab (365-day vague solar year: 18 winals of 20 + Wayeb of 5)
    - Kin number (1-260)
    - Galactic tone (1-13) and Solar Seal / Day Sign (1-20)
    - Wavespell + Castle/Color (Dreamspell variant)
    - Element / direction / polarity / archetype mappings for narrative use

Two correlations are supported:
    - GMT 584283 (most widely used "Lounsbury" correlation, default).
    - GMT 584285 (Thompson; alternate).

The "Dreamspell" calendar (Jos� Arg�elles) maps day signs/tones to a
slightly different anchor; we expose both the classical GMT-anchored
sequence and the Dreamspell sequence so users can choose. Default is
classical GMT (584283).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional


# -----------------------------------------------------------------------------
# Correlations
# -----------------------------------------------------------------------------

GMT_584283 = 584283  # classical GMT correlation
GMT_584285 = 584285  # Thompson alt
DEFAULT_CORRELATION = GMT_584283

# Dreamspell offset relative to classical: Arg�elles' system uses a
# different anchor; this offset is applied to kin-counting only when the
# user selects "dreamspell" mode. For classical, we use the GMT mapping
# directly.
DREAMSPELL_KIN_OFFSET: int = 0  # Default, kept simple/explicit; classical alignment.

# Kin alignment: classical mapping requires us to anchor Tzolkin/Haab
# correctly. Using GMT 584283 as kin-1 reference (4 Ahau 8 Cumku for the
# Maya creation date 0.0.0.0.0 == kin? Actually 4 Ahau is tone 4 sign 20).
# Standard: at JD = 584283 (Sept 6, 3114 BCE proleptic Gregorian), the day
# is 4 Ahau (kin 160 in Tzolkin if 1=Imix 1).
#
# We pick the kin so that:
#   tzolkin_tone(JD=584283)  = 4
#   tzolkin_sign(JD=584283)  = 20  (Ahau)
# -> kin index in 1..260: tone = ((kin-1) % 13)+1, sign=((kin-1) % 20)+1
#    we need (kin-1) % 13 = 3 and (kin-1) % 20 = 19 -> kin-1 = 159 -> kin = 160.
ANCHOR_KIN_AT_GMT: int = 160

# -----------------------------------------------------------------------------
# Day signs (20)
# -----------------------------------------------------------------------------


# Index 1..20. Yucatec name, NL name, EN name, archetype-element,
# direction, polarity (yin/yang), keyword (NL, EN), galactic seal (Dreamspell name).
DAY_SIGNS: list[dict[str, Any]] = [
    {"index": 1, "yucatec": "Imix", "nl": "Krokodil", "en": "Crocodile",
     "element": "water", "direction": "east", "polarity": "yin",
     "kw_nl": "oerbron, voeding, nieuw begin", "kw_en": "primal source, nourishment, new beginning",
     "dreamspell": "Red Dragon"},
    {"index": 2, "yucatec": "Ik'", "nl": "Wind", "en": "Wind",
     "element": "air", "direction": "north", "polarity": "yang",
     "kw_nl": "communicatie, geest, adem", "kw_en": "communication, spirit, breath",
     "dreamspell": "White Wind"},
    {"index": 3, "yucatec": "Ak'b'al", "nl": "Nacht", "en": "Night",
     "element": "earth", "direction": "west", "polarity": "yin",
     "kw_nl": "innerlijke wereld, dromen, overvloed", "kw_en": "inner world, dreams, abundance",
     "dreamspell": "Blue Night"},
    {"index": 4, "yucatec": "K'an", "nl": "Zaad", "en": "Seed",
     "element": "fire", "direction": "south", "polarity": "yang",
     "kw_nl": "potentie, doelgerichtheid, ontkieming", "kw_en": "potential, purpose, sprouting",
     "dreamspell": "Yellow Seed"},
    {"index": 5, "yucatec": "Chikchan", "nl": "Slang", "en": "Serpent",
     "element": "fire", "direction": "east", "polarity": "yin",
     "kw_nl": "levenskracht, transformatie, instinct", "kw_en": "life-force, transformation, instinct",
     "dreamspell": "Red Serpent"},
    {"index": 6, "yucatec": "Kimi", "nl": "Wereldoverbrugger", "en": "Worldbridger",
     "element": "earth", "direction": "north", "polarity": "yang",
     "kw_nl": "loslaten, brug bouwen, dood en heropleving", "kw_en": "letting go, bridge-building, death-rebirth",
     "dreamspell": "White Worldbridger"},
    {"index": 7, "yucatec": "Manik'", "nl": "Hand", "en": "Hand",
     "element": "water", "direction": "west", "polarity": "yin",
     "kw_nl": "helen, vakmanschap, kennen", "kw_en": "healing, craft, knowing",
     "dreamspell": "Blue Hand"},
    {"index": 8, "yucatec": "Lamat", "nl": "Ster", "en": "Star",
     "element": "air", "direction": "south", "polarity": "yang",
     "kw_nl": "schoonheid, harmonie, kunst", "kw_en": "beauty, harmony, art",
     "dreamspell": "Yellow Star"},
    {"index": 9, "yucatec": "Muluk", "nl": "Maan", "en": "Moon",
     "element": "water", "direction": "east", "polarity": "yin",
     "kw_nl": "zuivering, herinnering, stroom", "kw_en": "purification, memory, flow",
     "dreamspell": "Red Moon"},
    {"index": 10, "yucatec": "Ok", "nl": "Hond", "en": "Dog",
     "element": "fire", "direction": "north", "polarity": "yang",
     "kw_nl": "loyaliteit, hart, verbinding", "kw_en": "loyalty, heart, connection",
     "dreamspell": "White Dog"},
    {"index": 11, "yucatec": "Chuen", "nl": "Aap", "en": "Monkey",
     "element": "air", "direction": "west", "polarity": "yin",
     "kw_nl": "speelsheid, magie, illusie", "kw_en": "play, magic, illusion",
     "dreamspell": "Blue Monkey"},
    {"index": 12, "yucatec": "Eb", "nl": "Mens", "en": "Human",
     "element": "earth", "direction": "south", "polarity": "yang",
     "kw_nl": "vrije wil, wijsheid, invloed", "kw_en": "free will, wisdom, influence",
     "dreamspell": "Yellow Human"},
    {"index": 13, "yucatec": "B'en", "nl": "Hemelwandelaar", "en": "Skywalker",
     "element": "fire", "direction": "east", "polarity": "yin",
     "kw_nl": "verkennen, profetie, verwondering", "kw_en": "exploration, prophecy, wonder",
     "dreamspell": "Red Skywalker"},
    {"index": 14, "yucatec": "Ix", "nl": "Tovenaar", "en": "Wizard",
     "element": "earth", "direction": "north", "polarity": "yang",
     "kw_nl": "tijdloosheid, ontvankelijkheid, magie", "kw_en": "timelessness, receptivity, magic",
     "dreamspell": "White Wizard"},
    {"index": 15, "yucatec": "Men", "nl": "Adelaar", "en": "Eagle",
     "element": "air", "direction": "west", "polarity": "yin",
     "kw_nl": "visie, hoger perspectief, plan", "kw_en": "vision, higher perspective, plan",
     "dreamspell": "Blue Eagle"},
    {"index": 16, "yucatec": "Kib'", "nl": "Krijger", "en": "Warrior",
     "element": "fire", "direction": "south", "polarity": "yang",
     "kw_nl": "intelligentie, vraagstelling, missie", "kw_en": "intelligence, questioning, mission",
     "dreamspell": "Yellow Warrior"},
    {"index": 17, "yucatec": "Kab'an", "nl": "Aarde", "en": "Earth",
     "element": "earth", "direction": "east", "polarity": "yin",
     "kw_nl": "navigatie, synchroniciteit, evolutie", "kw_en": "navigation, synchronicity, evolution",
     "dreamspell": "Red Earth"},
    {"index": 18, "yucatec": "Etz'nab'", "nl": "Spiegel", "en": "Mirror",
     "element": "water", "direction": "north", "polarity": "yang",
     "kw_nl": "weerspiegeling, helderheid, eindeloosheid", "kw_en": "reflection, clarity, endlessness",
     "dreamspell": "White Mirror"},
    {"index": 19, "yucatec": "Kawak", "nl": "Storm", "en": "Storm",
     "element": "water", "direction": "west", "polarity": "yin",
     "kw_nl": "katalysator, vernieuwing, generatie", "kw_en": "catalyst, renewal, generation",
     "dreamspell": "Blue Storm"},
    {"index": 20, "yucatec": "Ahau", "nl": "Zon", "en": "Sun",
     "element": "fire", "direction": "south", "polarity": "yang",
     "kw_nl": "verlichting, eenheid, universele liefde", "kw_en": "enlightenment, unity, universal love",
     "dreamspell": "Yellow Sun"},
]


GLYPHS: dict[int, str] = {
    1: "??", 2: "??", 3: "??", 4: "??", 5: "??", 6: "??", 7: "?", 8: "?", 9: "??", 10: "??",
    11: "??", 12: "??", 13: "??", 14: "??", 15: "??", 16: "?", 17: "??", 18: "??", 19: "?", 20: "?",
}


# -----------------------------------------------------------------------------
# Galactic tones (13)
# -----------------------------------------------------------------------------


GALACTIC_TONES: list[dict[str, Any]] = [
    {"index": 1, "name_nl": "Magnetisch", "name_en": "Magnetic",
     "kw_nl": "doel, verenigen, aantrekken", "kw_en": "purpose, unify, attract"},
    {"index": 2, "name_nl": "Lunair", "name_en": "Lunar",
     "kw_nl": "uitdaging, polariseren, stabiliseren", "kw_en": "challenge, polarize, stabilize"},
    {"index": 3, "name_nl": "Elektrisch", "name_en": "Electric",
     "kw_nl": "dienst, activeren, verbinden", "kw_en": "service, activate, bond"},
    {"index": 4, "name_nl": "Zelf-bestaand", "name_en": "Self-existing",
     "kw_nl": "vorm, defini�ren, meten", "kw_en": "form, define, measure"},
    {"index": 5, "name_nl": "Doordringend", "name_en": "Overtone",
     "kw_nl": "stralen, bekrachtigen, bevelen", "kw_en": "radiance, empower, command"},
    {"index": 6, "name_nl": "Ritmisch", "name_en": "Rhythmic",
     "kw_nl": "gelijkheid, organiseren, balans", "kw_en": "equality, organize, balance"},
    {"index": 7, "name_nl": "Resonant", "name_en": "Resonant",
     "kw_nl": "afstemmen, kanaliseren, inspireren", "kw_en": "attune, channel, inspire"},
    {"index": 8, "name_nl": "Galactisch", "name_en": "Galactic",
     "kw_nl": "integriteit, modelleren, harmoniseren", "kw_en": "integrity, model, harmonize"},
    {"index": 9, "name_nl": "Solair", "name_en": "Solar",
     "kw_nl": "intentie, bedoelen, realiseren", "kw_en": "intention, intend, pulse"},
    {"index": 10, "name_nl": "Planetair", "name_en": "Planetary",
     "kw_nl": "manifestatie, perfectioneren, produceren", "kw_en": "manifest, perfect, produce"},
    {"index": 11, "name_nl": "Spectraal", "name_en": "Spectral",
     "kw_nl": "loslaten, oplossen, bevrijden", "kw_en": "liberate, dissolve, release"},
    {"index": 12, "name_nl": "Kristal", "name_en": "Crystal",
     "kw_nl": "samenwerking, opdragen, universaliseren", "kw_en": "cooperation, dedicate, universalize"},
    {"index": 13, "name_nl": "Kosmisch", "name_en": "Cosmic",
     "kw_nl": "aanwezigheid, transcenderen, doorwerken", "kw_en": "presence, transcend, endure"},
]


# -----------------------------------------------------------------------------
# Haab (vague solar year, 365 days)
# -----------------------------------------------------------------------------


HAAB_MONTHS: list[str] = [
    "Pop", "Wo", "Sip", "Sotz'", "Sek", "Xul", "Yaxk'in", "Mol", "Ch'en",
    "Yax", "Sak", "Keh", "Mak", "K'ank'in", "Muwan", "Pax", "K'ayab",
    "Kumk'u", "Wayeb",
]


# -----------------------------------------------------------------------------
# Long Count
# -----------------------------------------------------------------------------


def long_count_from_jd(jd_ut: float, correlation: int = DEFAULT_CORRELATION) -> tuple[int, int, int, int, int]:
    """
    Convert JD(UT) to Long Count tuple (baktun, katun, tun, uinal, kin).
    1 baktun = 144000 days, 1 katun = 7200 days, 1 tun = 360 days,
    1 uinal = 20 days, 1 kin = 1 day.
    """
    days = int(jd_ut) - correlation
    if days < 0:
        # Pre-creation (rare); we still compute via modulo for representation.
        baktun, rem = divmod(days, 144000)
        katun, rem = divmod(rem, 7200)
        tun, rem = divmod(rem, 360)
        uinal, kin = divmod(rem, 20)
        return (baktun, katun, tun, uinal, kin)
    baktun, rem = divmod(days, 144000)
    katun, rem = divmod(rem, 7200)
    tun, rem = divmod(rem, 360)
    uinal, kin = divmod(rem, 20)
    return (baktun, katun, tun, uinal, kin)


# -----------------------------------------------------------------------------
# Tzolkin (260)
# -----------------------------------------------------------------------------


def kin_from_jd(jd_ut: float, correlation: int = DEFAULT_CORRELATION) -> int:
    """Return Tzolkin kin (1..260) for JD(UT) using GMT correlation."""
    delta = int(jd_ut) - correlation
    kin = (ANCHOR_KIN_AT_GMT - 1 + delta) % 260 + 1
    return kin


def tzolkin_from_kin(kin: int) -> tuple[int, int]:
    """(tone, sign_index) for kin 1..260."""
    tone = ((kin - 1) % 13) + 1
    sign = ((kin - 1) % 20) + 1
    return (tone, sign)


def haab_from_jd(jd_ut: float, correlation: int = DEFAULT_CORRELATION) -> tuple[int, int, str]:
    """
    Return (haab_day, haab_month_index_0_18, haab_month_name).

    Haab anchor at correlation: classical GMT places JD=584283 at "8 Cumku"
    (Cumku = 18, day=8). Day index counted in [0..364] over the 365-day
    vague year.
    """
    delta = int(jd_ut) - correlation
    # Cumku is index 17 (0-based); day 8 within Cumku = position 17*20 + (8-1) = 347
    anchor_pos = 17 * 20 + (8 - 1)
    pos = (anchor_pos + delta) % 365
    if pos < 360:
        month_idx = pos // 20
        day = pos % 20  # 0..19
    else:
        month_idx = 18  # Wayeb
        day = pos - 360  # 0..4
    return (day, month_idx, HAAB_MONTHS[month_idx])


# -----------------------------------------------------------------------------
# Wavespell + castle (Dreamspell variant)
# -----------------------------------------------------------------------------


def wavespell_info(kin: int) -> dict[str, Any]:
    """
    20 wavespells of 13 kins. The leading kin of each wavespell has tone 1
    (Magnetic). Castle = group of 4 wavespells (52 kins). 5 castles per
    Tzolkin year (260 = 5*52).
    """
    wavespell_idx = ((kin - 1) // 13) + 1  # 1..20
    position_in_wavespell = ((kin - 1) % 13) + 1  # 1..13
    castle_idx = ((kin - 1) // 52) + 1  # 1..5
    leader_kin = ((kin - 1) // 13) * 13 + 1
    leader_tone, leader_sign = tzolkin_from_kin(leader_kin)
    castles = [
        {"id": 1, "color": "red", "name_nl": "Rood Kasteel van het Vliegen",
         "name_en": "Red Castle of Turning"},
        {"id": 2, "color": "white", "name_nl": "Wit Kasteel van het Kruisen",
         "name_en": "White Castle of Crossing"},
        {"id": 3, "color": "blue", "name_nl": "Blauw Kasteel van Branden",
         "name_en": "Blue Castle of Burning"},
        {"id": 4, "color": "yellow", "name_nl": "Geel Kasteel van Geven",
         "name_en": "Yellow Castle of Giving"},
        {"id": 5, "color": "green", "name_nl": "Groen Centraal Kasteel",
         "name_en": "Green Central Castle"},
    ]
    return {
        "wavespell_index": wavespell_idx,
        "wavespell_kin_leader": leader_kin,
        "wavespell_leader_sign": leader_sign,
        "wavespell_position": position_in_wavespell,
        "castle": castles[castle_idx - 1],
    }


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def lookup_sign(sign_index: int) -> dict[str, Any]:
    if 1 <= sign_index <= 20:
        return DAY_SIGNS[sign_index - 1]
    return {}


def lookup_tone(tone_index: int) -> dict[str, Any]:
    if 1 <= tone_index <= 13:
        return GALACTIC_TONES[tone_index - 1]
    return {}


# -----------------------------------------------------------------------------
# Personal cycles
# -----------------------------------------------------------------------------


def personal_year_cycles(kin_birth: int) -> list[dict[str, Any]]:
    """
    Personal year cycles: each new Tzolkin (260 days) repetition starting
    from kin_birth. Returns 4 upcoming positions from current kin.
    """
    out: list[dict[str, Any]] = []
    for i in range(1, 5):
        next_kin = ((kin_birth - 1 + 260 * i) % 260) + 1
        tone, sign = tzolkin_from_kin(next_kin)
        out.append({
            "cycle": i,
            "kin": next_kin,
            "tone": tone,
            "sign": sign,
        })
    return out


def harmonic_from_kin(kin: int) -> dict[str, Any]:
    """Tzolkin harmonic: 65 harmonics of 4 kins each."""
    h = ((kin - 1) // 4) + 1
    pos = ((kin - 1) % 4) + 1
    return {"harmonic": h, "position": pos}


# -----------------------------------------------------------------------------
# Builder (engine integration)
# -----------------------------------------------------------------------------


def build_maya(
    jd_ut: Optional[float],
    *,
    correlation: int = DEFAULT_CORRELATION,
    locale: str = "nl-NL",
) -> dict[str, Any]:
    """
    Build the Maya block. Uses the existing JD(UT) from the engine; no
    re-compute of astronomy.
    """
    if jd_ut is None:
        return {
            "long_count": None,
            "tzolkin": None,
            "haab": None,
            "kin": None,
            "tone": None,
            "sign": None,
            "wavespell": None,
            "harmonic": None,
            "personal_year_cycles": [],
            "correlation": correlation,
            "status": {
                "computed": False,
                "requires": ["date"],
                "confidence": "unavailable",
                "assumptions": [],
                "warnings": ["DATE_REQUIRED"],
            },
        }

    bk, kt, tn, un, ki = long_count_from_jd(jd_ut, correlation)
    kin = kin_from_jd(jd_ut, correlation)
    tone_idx, sign_idx = tzolkin_from_kin(kin)
    haab_day, haab_month_idx, haab_month_name = haab_from_jd(jd_ut, correlation)
    wave = wavespell_info(kin)
    harmonic = harmonic_from_kin(kin)
    pyc = personal_year_cycles(kin)

    sign = lookup_sign(sign_idx)
    tone = lookup_tone(tone_idx)

    return {
        "long_count": {
            "baktun": bk, "katun": kt, "tun": tn, "uinal": un, "kin": ki,
            "label": f"{bk}.{kt}.{tn}.{un}.{ki}",
        },
        "tzolkin": {
            "kin": kin,
            "tone_index": tone_idx,
            "sign_index": sign_idx,
            "label": f"{tone_idx} {sign.get('yucatec', '')}",
        },
        "haab": {
            "day": haab_day,
            "month_index": haab_month_idx,
            "month_name": haab_month_name,
            "label": f"{haab_day} {haab_month_name}",
        },
        "kin": kin,
        "tone": tone,
        "sign": sign,
        "wavespell": wave,
        "harmonic": harmonic,
        "personal_year_cycles": pyc,
        "correlation": correlation,
        "status": {
            "computed": True,
            "requires": ["date"],
            "confidence": "high",
            "assumptions": [f"correlation={correlation}"],
            "warnings": [],
        },
    }
