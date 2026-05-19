"""
Layer B/D - Human Design engine.

Lean, modular Human Design module that REUSES the existing astronomical
engine (astronomy.calc_planet_geocentric, time_scales). It adds NO duplicate
ephemeris code; it consumes already-computed planet longitudes and exposes
HD-specific structures: gates, lines, channels, centers, type, authority,
strategy, profile, incarnation cross.

Design (88-degree solar arc) chart:
    The Design chart is computed at the moment when the Sun was 88� (in
    ecliptic longitude) BEFORE birth. We resolve that JD by binary search
    against the geocentric solar longitude, then evaluate the same set of
    bodies as for the Personality (birth) chart.

Rave Mandala (gate-zodiac mapping):
    Sequence of 64 gates around the tropical zodiac. The wheel is anchored
    so that Gate 41 starts at 02�15'00" Aquarius (302.25� tropical
    longitude). Gate width is 360/64 = 5.625�, line width 5.625/6.

Output is JSON-serializable and intentionally narrative-friendly so the
energy_profile and interpretation layers can pull labels/keywords without
re-doing computation.
"""
from __future__ import annotations

import math
from typing import Any, Iterable, Optional

from . import astronomy as astro
from . import time_scales as ts


# -----------------------------------------------------------------------------
# Wheel constants
# -----------------------------------------------------------------------------

GATE_DEG: float = 360.0 / 64.0  # 5.625
LINE_DEG: float = GATE_DEG / 6.0  # 0.9375
COLOR_DEG: float = LINE_DEG / 6.0
TONE_DEG: float = COLOR_DEG / 5.0
BASE_DEG: float = TONE_DEG / 5.0

# Anchor: Gate 41 starts at 2�15' Aquarius (Aquarius starts at 300�)
WHEEL_ANCHOR_DEG: float = 302.25
WHEEL_ANCHOR_GATE: int = 41

# Gate sequence (zodiac order, increasing ecliptic longitude) starting at the
# anchor. Source: standard Rave Mandala used by the major HD calculators.
GATES_IN_WHEEL_ORDER: list[int] = [
    41, 19, 13, 49, 30, 55, 37, 63, 22, 36,
    25, 17, 21, 51, 42, 3, 27, 24, 2, 23,
    8, 20, 16, 35, 45, 12, 15, 52, 39, 53,
    62, 56, 31, 33, 7, 4, 29, 59, 40, 64,
    47, 6, 46, 18, 48, 57, 32, 50, 28, 44,
    1, 43, 14, 34, 9, 5, 26, 11, 10, 58,
    38, 54, 61, 60,
]

assert len(GATES_IN_WHEEL_ORDER) == 64
assert len(set(GATES_IN_WHEEL_ORDER)) == 64

# -----------------------------------------------------------------------------
# Gate metadata (canonical HD content)
# -----------------------------------------------------------------------------

# 9 centers, canonical HD set
CENTERS: tuple[str, ...] = (
    "Head", "Ajna", "Throat", "G", "Heart", "Spleen", "SolarPlexus", "Sacral", "Root",
)

# Gate -> center membership (canonical mapping)
GATE_CENTER: dict[int, str] = {
    # Head
    64: "Head", 61: "Head", 63: "Head",
    # Ajna
    47: "Ajna", 24: "Ajna", 4: "Ajna", 17: "Ajna", 43: "Ajna", 11: "Ajna",
    # Throat
    62: "Throat", 23: "Throat", 56: "Throat", 35: "Throat", 12: "Throat",
    45: "Throat", 33: "Throat", 8: "Throat", 31: "Throat", 7: "Throat",
    1: "Throat", 13: "Throat", 10: "Throat", 20: "Throat", 16: "Throat",
    # G center
    25: "G", 46: "G", 22: "G", 36: "G", 2: "G", 15: "G",  # 7,1,10,13 also touch G
    # Heart / Will
    21: "Heart", 40: "Heart", 26: "Heart", 51: "Heart",
    # Spleen
    48: "Spleen", 57: "Spleen", 44: "Spleen", 50: "Spleen", 32: "Spleen",
    28: "Spleen", 18: "Spleen",
    # Solar Plexus
    6: "SolarPlexus", 37: "SolarPlexus", 30: "SolarPlexus", 55: "SolarPlexus",
    49: "SolarPlexus", 39: "SolarPlexus", 41: "SolarPlexus",
    # Sacral
    34: "Sacral", 5: "Sacral", 14: "Sacral", 29: "Sacral", 59: "Sacral",
    9: "Sacral", 3: "Sacral", 42: "Sacral", 27: "Sacral",
    # Root
    53: "Root", 60: "Root", 52: "Root", 19: "Root", 38: "Root", 54: "Root",
    58: "Root",
}

# Gates that connect both to the Throat AND the G center via the central
# spine (1, 7, 10, 13 are dual-membership in HD bodygraphs). For activation
# logic we treat their "primary" center as G; channels enforce the actual
# defined relationship.
DUAL_CENTER_GATES: dict[int, tuple[str, str]] = {
    1: ("Throat", "G"),
    7: ("Throat", "G"),
    10: ("Throat", "G"),
    13: ("Throat", "G"),
}

# 36 canonical channels. Each entry: (gate_a, gate_b) -> channel name + circuit.
# Circuit: individual / tribal / collective_logic / collective_abstract /
# integration. Sub-keyword is the working theme.
CHANNELS: list[dict[str, Any]] = [
    {"gates": (1, 8), "name": "Inspiration", "circuit": "individual",
     "theme": "Creative role-modeling and authentic contribution"},
    {"gates": (2, 14), "name": "The Beat", "circuit": "individual",
     "theme": "Empowerment through rhythmic abundance"},
    {"gates": (3, 60), "name": "Mutation", "circuit": "individual",
     "theme": "Energy for change held by limitation"},
    {"gates": (4, 63), "name": "Logic", "circuit": "collective_logic",
     "theme": "Mental certainty through formulation"},
    {"gates": (5, 15), "name": "Rhythm", "circuit": "collective_logic",
     "theme": "Flow with the rhythms of life"},
    {"gates": (6, 59), "name": "Mating", "circuit": "tribal",
     "theme": "Intimacy via emotional friction and bonding"},
    {"gates": (7, 31), "name": "The Alpha", "circuit": "collective_logic",
     "theme": "Leadership for the sake of collective direction"},
    {"gates": (9, 52), "name": "Concentration", "circuit": "collective_logic",
     "theme": "Focused determination on details"},
    {"gates": (10, 20), "name": "Awakening", "circuit": "integration",
     "theme": "Self-love expressed in the now"},
    {"gates": (10, 34), "name": "Exploration", "circuit": "integration",
     "theme": "Following one's convictions"},
    {"gates": (10, 57), "name": "Perfected Form", "circuit": "integration",
     "theme": "Survival aligned with intuitive truth"},
    {"gates": (11, 56), "name": "Curiosity", "circuit": "collective_abstract",
     "theme": "Stimulating ideas through stories"},
    {"gates": (12, 22), "name": "Openness", "circuit": "individual",
     "theme": "Social passion expressed in perfect timing"},
    {"gates": (13, 33), "name": "The Prodigal", "circuit": "collective_abstract",
     "theme": "A witness reflecting collective experience"},
    {"gates": (16, 48), "name": "The Wave Length", "circuit": "collective_logic",
     "theme": "Talent grounded in mastery"},
    {"gates": (17, 62), "name": "Acceptance", "circuit": "collective_logic",
     "theme": "Logical opinion expressed through detail"},
    {"gates": (18, 58), "name": "Judgment", "circuit": "collective_logic",
     "theme": "Joyful drive to correct what is broken"},
    {"gates": (19, 49), "name": "Synthesis", "circuit": "tribal",
     "theme": "Sensitivity to needs and principled response"},
    {"gates": (20, 34), "name": "Charisma", "circuit": "integration",
     "theme": "Where thoughts must become deeds"},
    {"gates": (20, 57), "name": "The Brain Wave", "circuit": "integration",
     "theme": "Awareness embodied in present-time speech"},
    {"gates": (21, 45), "name": "Money", "circuit": "tribal",
     "theme": "Material world stewardship"},
    {"gates": (23, 43), "name": "Structuring", "circuit": "individual",
     "theme": "Insight expressed as individual knowing"},
    {"gates": (24, 61), "name": "Awareness", "circuit": "individual",
     "theme": "Mental thinker � knowing through wonder"},
    {"gates": (25, 51), "name": "Initiation", "circuit": "individual",
     "theme": "Need to be first; spiritual shock therapy"},
    {"gates": (26, 44), "name": "Surrender", "circuit": "tribal",
     "theme": "Transmitting messages with integrity"},
    {"gates": (27, 50), "name": "Preservation", "circuit": "tribal",
     "theme": "Custodianship of values and care"},
    {"gates": (28, 38), "name": "Struggle", "circuit": "individual",
     "theme": "Stubbornness in finding life's purpose"},
    {"gates": (29, 46), "name": "Discovery", "circuit": "collective_abstract",
     "theme": "Succeeding where others fail"},
    {"gates": (30, 41), "name": "Recognition", "circuit": "collective_abstract",
     "theme": "Focused emotional energy of fantasy"},
    {"gates": (32, 54), "name": "Transformation", "circuit": "tribal",
     "theme": "Drive for material ambition"},
    {"gates": (34, 57), "name": "Power", "circuit": "integration",
     "theme": "Pure archetype of empowered intuition"},
    {"gates": (35, 36), "name": "Transitoriness", "circuit": "collective_abstract",
     "theme": "Jack-of-all-trades; passing through experiences"},
    {"gates": (37, 40), "name": "Community", "circuit": "tribal",
     "theme": "Bargain between work and reward"},
    {"gates": (39, 55), "name": "Emoting", "circuit": "individual",
     "theme": "Spirit released through emotional moodiness"},
    {"gates": (42, 53), "name": "Maturation", "circuit": "collective_abstract",
     "theme": "Cycle completed by experience"},
    {"gates": (47, 64), "name": "Abstraction", "circuit": "collective_abstract",
     "theme": "Mental activity to make sense of the past"},
]

assert len(CHANNELS) == 36

# Gate -> short keyword (used in narrative engine). 64 entries.
GATE_KEYWORDS_NL: dict[int, str] = {
    1: "creatieve zelfexpressie", 2: "richting van het zelf",
    3: "innovatie door beperking", 4: "antwoorden formuleren",
    5: "vaste ritmes", 6: "wrijving en intimiteit",
    7: "rol van leiderschap", 8: "bijdragen met stijl",
    9: "concentratie op detail", 10: "liefde voor jezelf",
    11: "idee�n doorgeven", 12: "voorzichtig spreken",
    13: "luisterend getuige", 14: "kracht door rijkdom",
    15: "extremen omarmen", 16: "selectief talent",
    17: "logische mening", 18: "correctie en kritiek",
    19: "behoefte aan verbinding", 20: "het nu uitspreken",
    21: "controle over materie", 22: "openheid en charme",
    23: "individuele kennis delen", 24: "rationaliseren",
    25: "onschuld van de geest", 26: "trickster met integriteit",
    27: "zorg voor anderen", 28: "spel van het leven",
    29: "doorzettingsvermogen", 30: "wens en verlangen",
    31: "invloed door rol", 32: "waarde van continu�teit",
    33: "afgezonderd reflecteren", 34: "kracht in beweging",
    35: "verandering en ervaring", 36: "crisis als motor",
    37: "familie en bond", 38: "strijd voor zin",
    39: "provocatie", 40: "alleen en overgave",
    41: "verbeelding starten", 42: "afronden van cycli",
    43: "individueel inzicht", 44: "patronen herkennen",
    45: "verzamelen en delen", 46: "lichamelijke vreugde",
    47: "realisatie", 48: "diepte als bron",
    49: "principes en grenzen", 50: "waarden bewaken",
    51: "shock als groei", 52: "stilstaan", 53: "beginnen",
    54: "ambitie en zelfontwikkeling", 55: "geest en stemming",
    56: "verhalen vertellen", 57: "intu�tieve helderheid",
    58: "vitaliteit en kritiek", 59: "intimiteit doorbreken",
    60: "aanvaarden van limieten", 61: "innerlijke waarheid",
    62: "feiten in detail", 63: "twijfel en onderzoek",
    64: "verwerking van het verleden",
}

GATE_KEYWORDS_EN: dict[int, str] = {
    1: "creative self-expression", 2: "direction of self",
    3: "innovation through limitation", 4: "formulating answers",
    5: "fixed rhythms", 6: "friction and intimacy",
    7: "role of leadership", 8: "contributing with style",
    9: "focus on detail", 10: "love of self",
    11: "transmitting ideas", 12: "cautious expression",
    13: "the listener", 14: "power through wealth",
    15: "embracing extremes", 16: "selective talent",
    17: "logical opinion", 18: "correction and critique",
    19: "need for connection", 20: "speaking the now",
    21: "control of matter", 22: "openness and grace",
    23: "splitting individual knowing", 24: "rationalizing",
    25: "innocence of mind", 26: "trickster with integrity",
    27: "care of others", 28: "the game of life",
    29: "perseverance", 30: "desire and longing",
    31: "leading by influence", 32: "value of continuity",
    33: "private reflection", 34: "power in motion",
    35: "change through experience", 36: "crisis as motor",
    37: "family and bond", 38: "fight for meaning",
    39: "provocation", 40: "aloneness and surrender",
    41: "starting imagination", 42: "completing cycles",
    43: "individual insight", 44: "recognizing patterns",
    45: "gather and share", 46: "joy of body",
    47: "realisation", 48: "depth as resource",
    49: "principles and edges", 50: "guarding values",
    51: "shock as growth", 52: "stillness", 53: "beginning",
    54: "ambition and self-development", 55: "spirit and mood",
    56: "telling stories", 57: "intuitive clarity",
    58: "vitality and critique", 59: "breaking intimacy",
    60: "accepting limits", 61: "inner knowing",
    62: "facts in detail", 63: "doubt and inquiry",
    64: "processing the past",
}

CENTER_THEME_NL: dict[str, str] = {
    "Head": "inspiratiedruk, vragen, mentale druk",
    "Ajna": "denken, verwerken, conceptualiseren",
    "Throat": "manifestatie en communicatie",
    "G": "identiteit, liefde en richting",
    "Heart": "wilskracht en zelfvertrouwen",
    "Spleen": "intu�tie, gezondheid, overleving",
    "SolarPlexus": "emoties, golven, geest",
    "Sacral": "levenskracht, werk en vruchtbaarheid",
    "Root": "druk, adrenaline en ritme",
}
CENTER_THEME_EN: dict[str, str] = {
    "Head": "inspiration pressure, questioning, mental drive",
    "Ajna": "thinking, processing, conceptualizing",
    "Throat": "manifestation and communication",
    "G": "identity, love and direction",
    "Heart": "willpower and self-confidence",
    "Spleen": "intuition, health, survival",
    "SolarPlexus": "emotions, waves, spirit",
    "Sacral": "life-force, work and fertility",
    "Root": "pressure, adrenaline and rhythm",
}


# -----------------------------------------------------------------------------
# HD bodies (planets used in chart activations)
# -----------------------------------------------------------------------------

# Order matters for output: by HD convention Sun, Earth, North Node, South
# Node, Moon, then Mercury .. Pluto.
HD_BODY_ORDER: list[str] = [
    "Sun", "Earth", "NorthNode", "SouthNode", "Moon",
    "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto",
]


HD_BODY_TO_SE: dict[str, int] = {
    "Sun": astro.SE_SUN,
    "Moon": astro.SE_MOON,
    "Mercury": astro.SE_MERCURY,
    "Venus": astro.SE_VENUS,
    "Mars": astro.SE_MARS,
    "Jupiter": astro.SE_JUPITER,
    "Saturn": astro.SE_SATURN,
    "Uranus": astro.SE_URANUS,
    "Neptune": astro.SE_NEPTUNE,
    "Pluto": astro.SE_PLUTO,
    "NorthNode": astro.SE_TRUE_NODE,
}

# -----------------------------------------------------------------------------
# Wheel math
# -----------------------------------------------------------------------------


def _norm_deg(deg: float) -> float:
    return deg % 360.0


def gate_line_from_longitude(lon_deg: float) -> tuple[int, int, int, int]:
    """
    Map ecliptic longitude (tropical, deg) to Rave Mandala (gate, line, color, tone).
    Returns (gate, line, color, tone) -- subdivisions used for HD activations.
    """
    delta = _norm_deg(lon_deg - WHEEL_ANCHOR_DEG)
    gate_idx = int(delta // GATE_DEG) % 64
    gate = GATES_IN_WHEEL_ORDER[gate_idx]
    rest = delta - gate_idx * GATE_DEG
    line = int(rest // LINE_DEG) + 1
    if line > 6:
        line = 6
    rest_line = rest - (line - 1) * LINE_DEG
    color = int(rest_line // COLOR_DEG) + 1
    if color > 6:
        color = 6
    rest_color = rest_line - (color - 1) * COLOR_DEG
    tone = int(rest_color // TONE_DEG) + 1
    if tone > 5:
        tone = 5
    return (gate, line, color, tone)


def gate_keyword(gate: int, locale: Optional[str]) -> str:
    """Short keyword for a gate (used in narrative). Locale "nl" or "en"."""
    from .knowledgebase import locale_uses_english

    src = GATE_KEYWORDS_EN if locale_uses_english(locale) else GATE_KEYWORDS_NL
    return src.get(gate, "")


def center_theme(center: str, locale: Optional[str]) -> str:
    from .knowledgebase import locale_uses_english

    src = CENTER_THEME_EN if locale_uses_english(locale) else CENTER_THEME_NL
    return src.get(center, "")


# -----------------------------------------------------------------------------
# Design chart: time when Sun was 88� behind birth Sun
# -----------------------------------------------------------------------------


def _sun_lon_at_jd_tt(jd_tt: float) -> Optional[float]:
    lon, err = astro.solar_longitude_geocentric_deg(jd_tt)
    if err:
        return None
    return lon


def design_jd_tt_88deg_before(jd_tt_birth: float, sun_birth_deg: float) -> Optional[float]:
    """
    Find JD(TT) when geocentric Sun longitude was exactly 88� before
    sun_birth_deg in the natural direction of Sun motion (i.e. earlier in
    time, lower longitude modulo 360).

    Returns None if ephemeris is unavailable.
    """
    target_deg = _norm_deg(sun_birth_deg - 88.0)
    # Sun moves ~0.985�/day ? 88� corresponds to ~89.34 days.
    jd_lo = jd_tt_birth - 95.0
    jd_hi = jd_tt_birth - 80.0

    def _signed_diff(jd: float) -> Optional[float]:
        lon = _sun_lon_at_jd_tt(jd)
        if lon is None:
            return None
        d = (lon - target_deg) % 360.0
        if d > 180.0:
            d -= 360.0
        return d

    diff_lo = _signed_diff(jd_lo)
    diff_hi = _signed_diff(jd_hi)
    if diff_lo is None or diff_hi is None:
        return None

    # Expand window if not bracketing.
    expansions = 0
    while diff_lo * diff_hi > 0 and expansions < 10:
        if diff_hi < 0:
            jd_hi += 5.0
        else:
            jd_lo -= 5.0
        diff_lo = _signed_diff(jd_lo)
        diff_hi = _signed_diff(jd_hi)
        if diff_lo is None or diff_hi is None:
            return None
        expansions += 1

    for _ in range(60):
        jd_mid = 0.5 * (jd_lo + jd_hi)
        diff_mid = _signed_diff(jd_mid)
        if diff_mid is None:
            return None
        if abs(diff_mid) < 1e-7:
            return jd_mid
        if diff_lo * diff_mid <= 0:
            jd_hi = jd_mid
            diff_hi = diff_mid
        else:
            jd_lo = jd_mid
            diff_lo = diff_mid
        if jd_hi - jd_lo < 1e-7:
            return 0.5 * (jd_lo + jd_hi)
    return 0.5 * (jd_lo + jd_hi)


# -----------------------------------------------------------------------------
# Activation calculation for one chart (personality or design)
# -----------------------------------------------------------------------------


def _planet_lons_for_chart(jd_tt: float) -> dict[str, float]:
    """Return {body_id: ecliptic_lon_deg} for HD-relevant bodies at jd_tt."""
    out: dict[str, float] = {}
    for name, sid in HD_BODY_TO_SE.items():
        xx, err = astro.calc_planet_geocentric(jd_tt, sid)
        if err or not xx or xx[0] is None:
            continue
        out[name] = _norm_deg(float(xx[0]))
    if "Sun" in out:
        out["Earth"] = _norm_deg(out["Sun"] + 180.0)
    if "NorthNode" in out:
        out["SouthNode"] = _norm_deg(out["NorthNode"] + 180.0)
    return out


def _activations_from_lons(lons: dict[str, float]) -> dict[str, dict[str, Any]]:
    """For each body, derive (gate, line, color, tone)."""
    out: dict[str, dict[str, Any]] = {}
    for name in HD_BODY_ORDER:
        lon = lons.get(name)
        if lon is None:
            continue
        gate, line, color, tone = gate_line_from_longitude(lon)
        out[name] = {
            "lon_deg": lon,
            "gate": gate,
            "line": line,
            "color": color,
            "tone": tone,
        }
    return out


# -----------------------------------------------------------------------------
# Centers / channels / type / authority / strategy / profile
# -----------------------------------------------------------------------------


def _gates_from_activations(personality: dict[str, dict[str, Any]],
                            design: dict[str, dict[str, Any]]) -> set[int]:
    out: set[int] = set()
    for src in (personality, design):
        for body, data in src.items():
            g = data.get("gate")
            if isinstance(g, int):
                out.add(g)
    return out


def _active_channels(active_gates: set[int]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ch in CHANNELS:
        a, b = ch["gates"]
        if a in active_gates and b in active_gates:
            out.append({
                "gates": [a, b],
                "name": ch["name"],
                "circuit": ch["circuit"],
                "theme": ch["theme"],
            })
    return out


def _defined_centers(active_channels: list[dict[str, Any]]) -> set[str]:
    """A center is defined if a complete channel touches it."""
    defined: set[str] = set()
    for ch in active_channels:
        for g in ch["gates"]:
            ctr = GATE_CENTER.get(g)
            if ctr:
                defined.add(ctr)
            dual = DUAL_CENTER_GATES.get(g)
            if dual:
                defined.update(dual)
    return defined


# Centers categorized as "motors" in HD
MOTOR_CENTERS = {"Heart", "Sacral", "SolarPlexus", "Root"}

# Throat-connecting motor channels: any active channel that has one gate
# in the Throat and one in a motor center.
THROAT_MOTOR_CHANNELS = {
    (21, 45),  # Heart - Throat
    (35, 36),  # SolarPlexus - Throat
    (12, 22),  # SolarPlexus - Throat (12 throat, 22 G - actually emotional G; treat as via 22 SP? No - 22 is solar plexus)
    (23, 43),  # 43 Ajna -> 23 Throat (not motor, skip)
}


def _channel_link_centers(channel_gates: tuple[int, int]) -> tuple[str, str]:
    a, b = channel_gates
    ca = GATE_CENTER.get(a, "?")
    cb = GATE_CENTER.get(b, "?")
    return (ca, cb)


def _motor_to_throat_active(active_channels: list[dict[str, Any]]) -> bool:
    """Is there at least one motor center -> throat connection (direct or via spine)."""
    motor_centers = MOTOR_CENTERS
    defined = _defined_centers(active_channels)
    if "Throat" not in defined:
        return False
    # Look for any active channel where one end is a motor and the other is throat.
    for ch in active_channels:
        a, b = ch["gates"]
        ca, cb = _channel_link_centers((a, b))
        ends = {ca, cb}
        if ends & motor_centers and "Throat" in ends:
            return True
    # Also look for motor->throat through a chain of two channels (e.g. 34 sacral -> 20 throat directly is 34-20)
    # 34-20 already handled above.
    # Heart -> Throat via 21-45 handled.
    # Solar Plexus -> Throat via 35-36? 35 is Throat, 36 is SolarPlexus -> direct.
    # Solar Plexus -> Throat via 12-22? 12 is Throat, 22 is SolarPlexus.
    # Root -> Throat: via Root->Spleen->Throat? actually 18-58 root-spleen, 28-38 spleen-root. Spleen to throat? No.
    # Root -> Spleen -> Throat: through 28-38 (spleen-root) + (spleen-throat?) Spleen does not connect directly to throat.
    # So motor-to-throat for Manifestor is essentially Heart, Solar Plexus, or Sacral connection to throat.
    # The above already covers direct cases; longer chains are not standard HD type definitions.
    return False


def _has_sacral_defined(defined_centers: set[str]) -> bool:
    return "Sacral" in defined_centers


def hd_type(active_channels: list[dict[str, Any]]) -> str:
    """Return canonical HD type string."""
    defined = _defined_centers(active_channels)
    if not defined:
        return "Reflector"
    sacral = "Sacral" in defined
    motor_to_throat = _motor_to_throat_active(active_channels)
    if sacral and motor_to_throat:
        return "Manifesting Generator"
    if sacral:
        return "Generator"
    if motor_to_throat:
        return "Manifestor"
    return "Projector"


def hd_strategy(hd_type_str: str, locale: Optional[str]) -> dict[str, str]:
    from .knowledgebase import locale_uses_english

    nl = not locale_uses_english(locale)
    table = {
        "Manifestor": (
            "Inform: laat anderen weten dat je gaat handelen.",
            "Inform: let others know you are about to act.",
        ),
        "Generator": (
            "Wachten om te reageren: volg het sacrale ja/nee.",
            "Wait to respond: follow the sacral yes/no.",
        ),
        "Manifesting Generator": (
            "Reageer en informeer: snel testen, dan informeren.",
            "Respond and inform: test quickly, then inform.",
        ),
        "Projector": (
            "Wachten op uitnodiging om herkend en juist gevraagd te worden.",
            "Wait for invitation/recognition before sharing your gift.",
        ),
        "Reflector": (
            "Wacht een volledige maancyclus (~28 dagen) voor grote keuzes.",
            "Wait a full lunar cycle (~28 days) before major decisions.",
        ),
    }
    nl_text, en_text = table.get(hd_type_str, ("", ""))
    return {"value": hd_type_str, "text": nl_text if nl else en_text}


def hd_authority(defined_centers: set[str], hd_type_str: str) -> str:
    """Hierarchy: Solar Plexus ? Sacral ? Spleen ? Heart ? G ? Mental ? Lunar."""
    if "SolarPlexus" in defined_centers:
        return "Emotional"
    if "Sacral" in defined_centers:
        return "Sacral"
    if "Spleen" in defined_centers:
        return "Splenic"
    if "Heart" in defined_centers:
        return "Ego"
    if "G" in defined_centers:
        return "Self-projected"
    if hd_type_str == "Reflector":
        return "Lunar"
    return "Mental"


# Standard HD profile names (NL/EN)
PROFILE_NAMES: dict[tuple[int, int], dict[str, str]] = {
    (1, 3): {"nl": "Onderzoeker / Martelaar", "en": "Investigator / Martyr"},
    (1, 4): {"nl": "Onderzoeker / Opportunist", "en": "Investigator / Opportunist"},
    (2, 4): {"nl": "Eenling / Opportunist", "en": "Hermit / Opportunist"},
    (2, 5): {"nl": "Eenling / Ketter", "en": "Hermit / Heretic"},
    (3, 5): {"nl": "Martelaar / Ketter", "en": "Martyr / Heretic"},
    (3, 6): {"nl": "Martelaar / Rolmodel", "en": "Martyr / Role Model"},
    (4, 6): {"nl": "Opportunist / Rolmodel", "en": "Opportunist / Role Model"},
    (4, 1): {"nl": "Opportunist / Onderzoeker", "en": "Opportunist / Investigator"},
    (5, 1): {"nl": "Ketter / Onderzoeker", "en": "Heretic / Investigator"},
    (5, 2): {"nl": "Ketter / Eenling", "en": "Heretic / Hermit"},
    (6, 2): {"nl": "Rolmodel / Eenling", "en": "Role Model / Hermit"},
    (6, 3): {"nl": "Rolmodel / Martelaar", "en": "Role Model / Martyr"},
}


def hd_profile(personality: dict[str, dict[str, Any]],
               design: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Personality Sun line / Design Sun line."""
    p_line = personality.get("Sun", {}).get("line")
    d_line = design.get("Sun", {}).get("line")
    if not isinstance(p_line, int) or not isinstance(d_line, int):
        return {"value": None, "label_nl": "", "label_en": ""}
    key = f"{p_line}/{d_line}"
    names = PROFILE_NAMES.get((p_line, d_line), {"nl": "", "en": ""})
    return {
        "value": key,
        "personality_line": p_line,
        "design_line": d_line,
        "label_nl": names.get("nl", ""),
        "label_en": names.get("en", ""),
    }


def _angle_kind(p_line: Optional[int], d_line: Optional[int]) -> str:
    if not isinstance(p_line, int) or not isinstance(d_line, int):
        return "unknown"
    s = {p_line, d_line}
    if s == {4, 6} or s == {6, 4} or s == {1, 4} or s == {2, 5} or s == {3, 6}:
        # Juxtaposition is only 4/1; left angle has 4/6,5/1,5/2,6/2,6/3,4/6 etc.
        pass
    if (p_line, d_line) == (4, 1):
        return "juxtaposition"
    LEFT = {(2, 4), (1, 3), (1, 4), (3, 5), (2, 5), (4, 6), (3, 6), (5, 6)}
    if (p_line, d_line) in LEFT or (d_line, p_line) in LEFT:
        return "left"
    return "right"


def hd_incarnation_cross(personality: dict[str, dict[str, Any]],
                         design: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return canonical incarnation cross identification."""
    p_sun = personality.get("Sun", {}).get("gate")
    p_earth = personality.get("Earth", {}).get("gate")
    d_sun = design.get("Sun", {}).get("gate")
    d_earth = design.get("Earth", {}).get("gate")
    p_line = personality.get("Sun", {}).get("line")
    d_line = design.get("Sun", {}).get("line")
    angle = _angle_kind(p_line, d_line)
    angle_label = {
        "right": "Right Angle Cross",
        "left": "Left Angle Cross",
        "juxtaposition": "Juxtaposition Cross",
        "unknown": "Cross",
    }[angle]
    return {
        "angle": angle,
        "label": angle_label,
        "personality_sun": p_sun,
        "personality_earth": p_earth,
        "design_sun": d_sun,
        "design_earth": d_earth,
        "name_short": (
            f"{angle_label} ({p_sun}/{p_earth} | {d_sun}/{d_earth})"
            if all(isinstance(g, int) for g in (p_sun, p_earth, d_sun, d_earth))
            else angle_label
        ),
    }


# -----------------------------------------------------------------------------
# Public top-level builder
# -----------------------------------------------------------------------------


def build_human_design(
    jd_tt_birth: Optional[float],
    *,
    locale: str = "nl-NL",
) -> dict[str, Any]:
    """
    Build the full Human Design block.

    jd_tt_birth: Terrestrial Time Julian Day at birth (already corrected by
                 the upstream engine for delta-T / EOP). When None or
                 ephemeris unavailable, returns a structured "unavailable"
                 block consistent with the rest of the engine.

    Returns a dict suitable for JSON serialization, with the same status
    contract used by the western/vedic/chinese blocks.
    """
    if jd_tt_birth is None:
        return _empty_block(["date", "time"], "TIME_REQUIRED")

    sun_birth_lon = _sun_lon_at_jd_tt(jd_tt_birth)
    if sun_birth_lon is None:
        return _empty_block(["date", "time"], "EPHEMERIS_UNAVAILABLE")

    jd_tt_design = design_jd_tt_88deg_before(jd_tt_birth, sun_birth_lon)
    if jd_tt_design is None:
        return _empty_block(["date", "time"], "DESIGN_RESOLVE_FAILED")

    pers_lons = _planet_lons_for_chart(jd_tt_birth)
    des_lons = _planet_lons_for_chart(jd_tt_design)
    if not pers_lons or not des_lons:
        return _empty_block(["date", "time"], "EPHEMERIS_UNAVAILABLE")

    personality = _activations_from_lons(pers_lons)
    design = _activations_from_lons(des_lons)

    active_gates = _gates_from_activations(personality, design)
    active_channels = _active_channels(active_gates)
    defined = _defined_centers(active_channels)
    undefined = [c for c in CENTERS if c not in defined]

    type_str = hd_type(active_channels)
    auth = hd_authority(defined, type_str)
    strat = hd_strategy(type_str, locale)
    profile = hd_profile(personality, design)
    cross = hd_incarnation_cross(personality, design)

    # Per-gate contribution map (used for SVG bodygraph + narrative).
    gate_sources: dict[int, list[dict[str, Any]]] = {}
    for chart_name, chart in (("personality", personality), ("design", design)):
        for body, data in chart.items():
            g = data.get("gate")
            if not isinstance(g, int):
                continue
            gate_sources.setdefault(g, []).append({
                "chart": chart_name,
                "body": body,
                "line": data.get("line"),
                "color": data.get("color"),
                "tone": data.get("tone"),
                "lon_deg": data.get("lon_deg"),
            })

    return {
        "type": type_str,
        "strategy": strat,
        "authority": auth,
        "profile": profile,
        "incarnation_cross": cross,
        "centers": {
            "defined": sorted(defined),
            "undefined": undefined,
            "all": list(CENTERS),
        },
        "channels": active_channels,
        "active_gates": sorted(active_gates),
        "gate_sources": {str(k): v for k, v in sorted(gate_sources.items())},
        "personality": personality,
        "design": design,
        "design_chart_jd_tt": jd_tt_design,
        "wheel": {
            "anchor_deg": WHEEL_ANCHOR_DEG,
            "anchor_gate": WHEEL_ANCHOR_GATE,
            "gate_width_deg": GATE_DEG,
        },
        "status": {
            "computed": True,
            "requires": ["date", "time"],
            "confidence": "high",
            "assumptions": [],
            "warnings": [],
        },
    }


def _empty_block(requires: list[str], code: str) -> dict[str, Any]:
    return {
        "type": None,
        "strategy": None,
        "authority": None,
        "profile": None,
        "incarnation_cross": None,
        "centers": {"defined": [], "undefined": list(CENTERS), "all": list(CENTERS)},
        "channels": [],
        "active_gates": [],
        "gate_sources": {},
        "personality": {},
        "design": {},
        "design_chart_jd_tt": None,
        "wheel": None,
        "status": {
            "computed": False,
            "requires": requires,
            "confidence": "unavailable",
            "assumptions": [],
            "warnings": [code],
        },
    }
