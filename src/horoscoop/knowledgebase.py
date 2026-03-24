"""
Seed knowledgebase for interpretations.

This project currently doesn't ship a populated SQL KB, so we provide an
embedded "baseline" knowledgebase as deterministic lookup tables.

Later, you can replace/augment these tables by loading from a DB and/or
evaluating kb_interp_trigger.trigger_json.
"""

from __future__ import annotations

from typing import Literal, Optional

Lang = Literal["nl", "en"]


def normalize_locale(locale: Optional[str]) -> Lang:
    if not locale:
        return "nl"
    loc = locale.lower()
    if loc.startswith("en"):
        return "en"
    return "nl"


ASPECT_MEANINGS: dict[str, dict[Lang, str]] = {
    "conjunction": {
        "nl": "Een conjunctie brengt twee krachten dicht bij elkaar: je ervaart sterke vermenging, overlap en focus van energie.",
        "en": "A conjunction brings two factors close together: you experience strong blending, overlap, and concentrated energy.",
    },
    "sextile": {
        "nl": "Een sextiel werkt vaak ondersteunend: het maakt samenwerking makkelijker en helpt kansen te benutten.",
        "en": "A sextile is often supportive: it makes cooperation easier and helps you seize opportunities.",
    },
    "square": {
        "nl": "Een vierkant geeft spanning en 'push': het zet je aan tot verandering, maar vraagt bewustheid om frictie vruchtbaar te maken.",
        "en": "A square adds tension and pressure: it pushes you toward change, but asks for awareness to turn friction into growth.",
    },
    "trine": {
        "nl": "Een driehoek voelt vloeiend: talenten stromen relatief makkelijk en geven gevoel van harmonie of vanzelfsprekendheid.",
        "en": "A trine feels flowing: strengths tend to move relatively easily and create a sense of ease or harmony.",
    },
    "opposition": {
        "nl": "Een oppositie laat twee polen tegenover elkaar staan: het vraagt balans, dialoog en integratie van tegengestelde behoeften.",
        "en": "An opposition sets two poles against each other: it calls for balance, dialogue, and integrating different needs.",
    },
    # Extended (optional)
    "semi-square": {
        "nl": "Een half- vierkant: subtiele frictie die je ritme uitdaagt en je leert bijstellen zonder te forceren.",
        "en": "A semi-square: subtle friction that challenges your rhythm and teaches you to adjust without forcing.",
    },
    "sesquiquadrate": {
        "nl": "Een anderhalf-vierkant: intensiteit en 'bijna' spanning, vaak voelbaar als een herhaald leerproces.",
        "en": "A sesquiquadrate: intensity and 'almost' tension, often felt as a repeated learning process.",
    },
    "quincunx": {
        "nl": "Een quincunx: het vraagt afstemming tussen verschillende waarden of prioriteiten; je groeit door bijsturen.",
        "en": "A quincunx: it asks for adjustment between different values or priorities; you grow by fine-tuning.",
    },
}


# Western zodiac sign meanings (tropical/sidereal share the same archetype)
SIGN_MEANINGS: dict[str, dict[Lang, str]] = {
    "Aries": {
        "nl": "Ram: initiatief, lef en doorzetten. Je groeit door actie en beweging om betekenis te creëren.",
        "en": "Aries: initiative, courage, and drive. You grow through action and motion to create meaning.",
    },
    "Taurus": {
        "nl": "Stier: stabiliteit, zintuigen en waardering. Je bloeit door consistentie, aandacht en iets echt maken.",
        "en": "Taurus: stability, senses, and appreciation. You thrive through consistency, attention, and making things real.",
    },
    "Gemini": {
        "nl": "Tweelingen: nieuwsgierigheid, uitwisseling en leren. Je energie beweegt via gesprekken en ideeën.",
        "en": "Gemini: curiosity, exchange, and learning. Your energy moves through conversation and ideas.",
    },
    "Cancer": {
        "nl": "Kreeft: gevoeligheid, veiligheid en zorg. Je groeit door emotioneel 'thuiskomen' en betrouwbare verbondenheid.",
        "en": "Cancer: sensitivity, safety, and care. You grow through emotional belonging and reliable connection.",
    },
    "Leo": {
        "nl": "Leeuw: creativiteit, trots en zichtbaar worden. Je bloeit wanneer je je hart volgt en iets deelt met warmte.",
        "en": "Leo: creativity, pride, and visibility. You thrive when you follow your heart and share with warmth.",
    },
    "Virgo": {
        "nl": "Maagd: ordening, verfijning en dienstbaarheid. Je groeit door verbeteren: kleine stappen, kwaliteit en vakmanschap.",
        "en": "Virgo: order, refinement, and service. You grow through improvement: small steps, quality, and craft.",
    },
    "Libra": {
        "nl": "Weegschaal: relaties, balans en schoonheid. Je ontwikkelt via afstemming en het vinden van het juiste midden.",
        "en": "Libra: relationships, balance, and beauty. You develop through alignment and finding the right middle.",
    },
    "Scorpio": {
        "nl": "Schorpioen: diepte, transformatie en waarheid. Je leert door door te breken naar kernlagen.",
        "en": "Scorpio: depth, transformation, and truth. You learn by breaking through to core layers.",
    },
    "Sagittarius": {
        "nl": "Boogschutter: visie, avontuur en betekenis. Je beweegt door leren, verkennen en richting kiezen.",
        "en": "Sagittarius: vision, adventure, and meaning. You move through learning, exploring, and choosing direction.",
    },
    "Capricorn": {
        "nl": "Steenbok: ambitie, verantwoordelijkheid en opbouw. Je groeit via structuur, discipline en focus op lange termijn.",
        "en": "Capricorn: ambition, responsibility, and construction. You grow through structure, discipline, and long-term focus.",
    },
    "Aquarius": {
        "nl": "Waterman: vernieuwing, vrijheid en toekomstdenken. Je zoekt ruimte om te experimenteren met nieuwe ideeën.",
        "en": "Aquarius: innovation, freedom, and future-thinking. You seek room to experiment with new ideas.",
    },
    "Pisces": {
        "nl": "Vissen: intuïtie, compassie en verbeelding. Je ontwikkelt via gevoeligheid en het omzetten van droom in betekenis.",
        "en": "Pisces: intuition, compassion, and imagination. You develop through sensitivity and turning dreams into meaning.",
    },
}


PLANET_MEANINGS: dict[str, dict[Lang, str]] = {
    "Sun": {
        "nl": "De Zon staat voor identiteit, levensenergie en richting: waar je 'ja' op zegt en waar je zelfvertrouwen vandaan komt.",
        "en": "The Sun stands for identity, life force, and direction: what you say yes to and where confidence comes from.",
    },
    "Moon": {
        "nl": "De Maan staat voor emotionele behoeften, ritme en instinct: hoe je voelt, herstelt en reageert.",
        "en": "The Moon represents emotional needs, rhythm, and instinct: how you feel, recover, and react.",
    },
    "Mercury": {
        "nl": "Mercurius staat voor denken, communicatie en uitwisseling: hoe je informatie verwerkt en betekenis vormt.",
        "en": "Mercury reflects thinking, communication, and exchange: how you process information and create meaning.",
    },
    "Venus": {
        "nl": "Venus staat voor liefde, verbinding en esthetiek: wat je aantrekt, waardeert en harmoniseert.",
        "en": "Venus relates to love, connection, and aesthetics: what you attract, value, and harmonize.",
    },
    "Mars": {
        "nl": "Mars staat voor drive, moed en initiatief: waar je actie op neemt en grenzen durft verleggen.",
        "en": "Mars is about drive, courage, and initiative: where you take action and dare to push boundaries.",
    },
    "Jupiter": {
        "nl": "Jupiter staat voor groei, betekenis en mogelijkheden: waar je kansen ziet en uitbreidt.",
        "en": "Jupiter stands for growth, meaning, and possibilities: where you see opportunities and expand.",
    },
    "Saturn": {
        "nl": "Saturnus staat voor structuur, verantwoordelijkheid en leerprocessen: waar je volwassenheid bouwt door discipline.",
        "en": "Saturn represents structure, responsibility, and learning: where maturity is built through discipline.",
    },
    # Special handling
    "Asc": {
        "nl": "De Ascendant beschrijft hoe je verschijnt en start: je 'eerste signaal' en je benadering van nieuwe situaties.",
        "en": "The Ascendant describes how you come across and begin: your first signal and your approach to new situations.",
    },
    "Ascendant": {
        "nl": "De Ascendant beschrijft hoe je verschijnt en start: je 'eerste signaal' en je benadering van nieuwe situaties.",
        "en": "The Ascendant describes how you come across and begin: your first signal and your approach to new situations.",
    },
}


HOUSE_MEANINGS: dict[int, dict[Lang, str]] = {
    1: {"nl": "Huis 1 gaat over zelfbeeld, uitstraling en initiatie: hoe jij de wereld binnenkomt.", "en": "House 1 is about self-image, presence, and initiation: how you enter the world."},
    2: {"nl": "Huis 2 gaat over waarden, bezit en persoonlijke hulpbronnen: waar je 'zekerheid' zoekt.", "en": "House 2 covers values, possessions, and personal resources: where you seek security."},
    3: {"nl": "Huis 3 gaat over communicatie, leren en korte reizen: je manier van denken delen.", "en": "House 3 relates to communication, learning, and short trips: how you share your mind."},
    4: {"nl": "Huis 4 gaat over thuis, basis en innerlijke veiligheid: de plek waar je wortelt.", "en": "House 4 is about home, foundations, and inner safety: where you take root."},
    5: {"nl": "Huis 5 gaat over creativiteit, plezier en risico nemen: hoe je jezelf laat zien.", "en": "House 5 is creativity, joy, and creative risk-taking: how you express yourself."},
    6: {"nl": "Huis 6 gaat over routines, gezondheid en dienstbaarheid: je dagelijks 'meesterschap'.", "en": "House 6 is routines, health, and service: your daily craftsmanship."},
    7: {"nl": "Huis 7 gaat over partnerschap, contracten en spiegelrelaties: wat je met 'de ander' leert.", "en": "House 7 is partnerships, contracts, and mirror relationships: what you learn with 'the other'."},
    8: {"nl": "Huis 8 gaat over transformatie, gedeelde middelen en intimiteit: waar je doorbreekt naar diepte.", "en": "House 8 is transformation, shared resources, and intimacy: where you break into depth."},
    9: {"nl": "Huis 9 gaat over betekenis, geloof en verdieping: je zoektocht naar een grotere visie.", "en": "House 9 is meaning, belief, and depth: your search for a bigger vision."},
    10: {"nl": "Huis 10 gaat over carrière, richting en reputatie: wat je zichtbaar opbouwt.", "en": "House 10 is career, direction, and reputation: what you build publicly."},
    11: {"nl": "Huis 11 gaat over netwerk, doelen en toekomstvisie: waar je samen vooruit beweegt.", "en": "House 11 covers networks, goals, and future: where you move forward together."},
    12: {"nl": "Huis 12 gaat over achtergronden, innerlijke verwerking en soms terugtrekking: wijsheid via stilte.", "en": "House 12 is hidden processes, inner processing, and sometimes retreat: wisdom through quiet."},
}


# Chinese: stems and branches (transliteration + concise keywords)
CHINESE_STEMS: list[str] = [
    "Jiǎ",
    "Yǐ",
    "Bǐng",
    "Dīng",
    "Wù",
    "Jǐ",
    "Gēng",
    "Xīn",
    "Rén",
    "Guǐ",
]

CHINESE_BRANCHES: list[str] = [
    "Zǐ",
    "Chǒu",
    "Yín",
    "Mǎo",
    "Chén",
    "Sì",
    "Wǔ",
    "Wèi",
    "Shēn",
    "Yǒu",
    "Xū",
    "Hài",
]

CHINESE_STEM_MEANINGS: dict[str, dict[Lang, str]] = {
    "Jiǎ": {"nl": "Jiǎ (Yang Hout): pionieren, starten, pioniersenergie en groei door initiatief.", "en": "Jiǎ (Yang Wood): pioneer spirit, beginnings, and growth through initiative."},
    "Yǐ": {"nl": "Yǐ (Yin Hout): verfijning, vormgeven en groei door geduldige ontwikkeling.", "en": "Yǐ (Yin Wood): refinement, shaping, and growth through patience."},
    "Bǐng": {"nl": "Bǐng (Yang Vuur): inspiratie, expressie en het 'aanzetten' van bewust leven.", "en": "Bǐng (Yang Fire): inspiration, expression, and igniting conscious life."},
    "Dīng": {"nl": "Dīng (Yin Vuur): aandacht, discipline en warmte met focus.", "en": "Dīng (Yin Fire): attention, discipline, and focused warmth."},
    "Wù": {"nl": "Wù (Yang Aarde): stabiliteit, ordening en het bouwen van duurzame fundamenten.", "en": "Wù (Yang Earth): stability, structuring, and building durable foundations."},
    "Jǐ": {"nl": "Jǐ (Yin Aarde): beheer, oog voor detail en voeding op langere termijn.", "en": "Jǐ (Yin Earth): management, attention to detail, and long-term nourishment."},
    "Gēng": {"nl": "Gēng (Yang Metaal): heldere grenzen, daadkracht en het scherpstellen van doelen.", "en": "Gēng (Yang Metal): clear boundaries, decisive action, and sharpening goals."},
    "Xīn": {"nl": "Xīn (Yin Metaal): precisie, waarde-oordeel en verfijning van keuzes.", "en": "Xīn (Yin Metal): precision, valuation, and refining decisions."},
    "Rén": {"nl": "Rén (Yang Water): mededogen, inzicht en intuïtieve stroming.", "en": "Rén (Yang Water): compassion, insight, and intuitive flow."},
    "Guǐ": {"nl": "Guǐ (Yin Water): diepte, vorm in emoties en verwerking via aandacht.", "en": "Guǐ (Yin Water): depth, shaping emotions, and processing through attention."},
}

CHINESE_BRANCH_MEANINGS: dict[str, dict[Lang, str]] = {
    "Zǐ": {"nl": "Zǐ (Rat): start van een cyclus, mentale scherpte en strategisch denken.", "en": "Zǐ (Rat): cycle beginnings, mental sharpness, and strategic thinking."},
    "Chǒu": {"nl": "Chǒu (Os): geduld, standvastigheid en bouwen met consistentie.", "en": "Chǒu (Ox): patience, steadiness, and building with consistency."},
    "Yín": {"nl": "Yín (Tijger): moed, beweging en creatie van energie door actie.", "en": "Yín (Tiger): courage, movement, and creating energy through action."},
    "Mǎo": {"nl": "Mǎo (Konijn): sensitiviteit, zachtheid en sociale harmonie.", "en": "Mǎo (Rabbit): sensitivity, gentleness, and social harmony."},
    "Chén": {"nl": "Chén (Draak): groei, potentie en het samenbrengen van mogelijkheden.", "en": "Chén (Dragon): growth, potential, and gathering possibilities."},
    "Sì": {"nl": "Sì (Slang): focus, wijsheid en transformatie via bewuste aandacht.", "en": "Sì (Snake): focus, wisdom, and transformation through mindful attention."},
    "Wǔ": {"nl": "Wǔ (Paard): vitaliteit, snelheid en richting in levenstempo.", "en": "Wǔ (Horse): vitality, speed, and direction in life rhythm."},
    "Wèi": {"nl": "Wèi (Geit): creativiteit, samenwerking en draagkracht in relaties.", "en": "Wèi (Goat): creativity, collaboration, and relational endurance."},
    "Shēn": {"nl": "Shēn (Aap): onderzoek, adaptatie en leren door variatie.", "en": "Shēn (Monkey): investigation, adaptability, and learning through variety."},
    "Yǒu": {"nl": "Yǒu (Haan): waakzaamheid, eerlijkheid en helderheid in communicatie.", "en": "Yǒu (Rooster): vigilance, honesty, and clarity in communication."},
    "Xū": {"nl": "Xū (Hond): loyaliteit, bescherming en betrouwbaarheid in vertrouwen.", "en": "Xū (Dog): loyalty, protection, and reliability in trust."},
    "Hài": {"nl": "Hài (Varken): ontspanning, vrijgevigheid en herstel door zachte energie.", "en": "Hài (Pig): relaxation, generosity, and recovery through gentle energy."},
}


def chinese_pillar_meaning(locale: Lang, *, pillar_label: str, stem: str, branch: str) -> str:
    stem_txt = CHINESE_STEM_MEANINGS.get(stem, {}).get(locale, stem)
    branch_txt = CHINESE_BRANCH_MEANINGS.get(branch, {}).get(locale, branch)
    if locale == "nl":
        return (
            f"{pillar_label}: {stem_txt} en {branch_txt}. "
            "Dit laat zien hoe die cycluslaag energie draagt in je leven. "
            "Je merkt het vooral doordat je ritme, focus en gevoeligheid verschuiven richting wat 'logisch' voelt voor dat moment."
        )
    return (
        f"{pillar_label}: {stem_txt} and {branch_txt}. "
        "This describes how that cycle layer carries energy in your life. "
        "You tend to notice it through changes in rhythm, priorities, and sensitivity that feel natural for that moment."
    )


VAARA_MEANINGS: dict[str, dict[Lang, str]] = {
    "Sunday": {"nl": "Zondag (Vaara): een sfeer van rust, betekenis en innerlijke verbinding.", "en": "Sunday (Vaara): a tone of calm, meaning, and inner connection."},
    "Monday": {"nl": "Maandag (Vaara): emoties, gevoeligheid en groei door verwerking.", "en": "Monday (Vaara): emotions, sensitivity, and growth through processing."},
    "Tuesday": {"nl": "Dinsdag (Vaara): actie, moed en momentum voor initiatief.", "en": "Tuesday (Vaara): action, courage, and momentum for initiative."},
    "Wednesday": {"nl": "Woensdag (Vaara): denken, leren en communicatie die richting geeft.", "en": "Wednesday (Vaara): thinking, learning, and communication that sets direction."},
    "Thursday": {"nl": "Donderdag (Vaara): expansie, hoop en 'zegen'-kwaliteit in je plannen.", "en": "Thursday (Vaara): expansion, hope, and a 'blessing' quality in your plans."},
    "Friday": {"nl": "Vrijdag (Vaara): relatie, liefde, charme en creatieve aantrekkingskracht.", "en": "Friday (Vaara): relationships, love, charm, and creative attraction."},
    "Saturday": {"nl": "Zaterdag (Vaara): discipline, overzicht en constructieve stappen naar stabiliteit.", "en": "Saturday (Vaara): discipline, overview, and constructive steps toward stability."},
}


# Karana: engine levert indices 1..60. We geven baseline betekenissen per index-groep.
KARANA_MEANINGS: dict[int, dict[Lang, str]] = {}
for _i in range(1, 61):
    group = (_i - 1) // 10  # 0..5
    if group == 0:
        nl = f"Karana {_i}: een fase van opstart en 'aanzetten'-energie krijgt een eerste vorm."
        en = f"Karana {_i}: a start-up phase-energy gains its first shape."
    elif group == 1:
        nl = f"Karana {_i}: expressie en afstemming-je leert door proberen en bij te sturen."
        en = f"Karana {_i}: expression and adjustment-learning through trial and fine-tuning."
    elif group == 2:
        nl = f"Karana {_i}: focus en verfijning-je wordt gevraagd om heldere keuzes te maken."
        en = f"Karana {_i}: focus and refinement-clarity through chosen direction."
    elif group == 3:
        nl = f"Karana {_i}: momentum en intensivering-dingen bewegen sneller, maar vragen overzicht."
        en = f"Karana {_i}: momentum and intensification-things move faster and need oversight."
    elif group == 4:
        nl = f"Karana {_i}: consolidatie en stabiliteit-je bouwt verder en maakt het stevig."
        en = f"Karana {_i}: consolidation and stability-build on and make it sturdy."
    else:
        nl = f"Karana {_i}: afronding en transformatie-je sluit iets af en maakt ruimte."
        en = f"Karana {_i}: closure and transformation-you finish something and make room."
    KARANA_MEANINGS[_i] = {"nl": nl, "en": en}


# Vedic: tithi 1..30 (baseline)
TITHI_MEANINGS: dict[int, dict[Lang, str]] = {}
for _i in range(1, 31):
    # Baseline grouping: wax/crystal-ish vs finish/turning.
    if _i <= 10:
        nl = f"Tithi {_i}: een fase van opbouw en groei-energie wordt 'opgepakt' en verfijnt richting actie."
        en = f"Tithi {_i}: a phase of building and growth-energy gets picked up and refined toward action."
    elif _i <= 20:
        nl = f"Tithi {_i}: een fase van expressie en afstemming-je voelt de dynamiek en leert doseren."
        en = f"Tithi {_i}: a phase of expression and adjustment-you feel the dynamics and learn pacing."
    else:
        nl = f"Tithi {_i}: een fase van consolidatie en transformatie-je sluit af, maakt ruimte en stuurt bij."
        en = f"Tithi {_i}: a phase of consolidation and transformation-you wrap up, make room, and readjust."
    TITHI_MEANINGS[_i] = {"nl": nl, "en": en}


# Nakshatra 1..27 (names + concise keywords; transliterations kept)
NAKSHATRA_NAMES_EN: list[str] = [
    "Aswini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashirsha",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

NAKSHATRA_KEYWORDS_EN: list[str] = [
    "healing & beginnings",
    "nourishment & sustainment",
    "purification & sharp focus",
    "growth & magnetism",
    "seeking & gentle curiosity",
    "change & awakenings",
    "return & renewed hope",
    "support & nourishment",
    "bonding & deep instincts",
    "authority & joy of mastery",
    "creativity & inner joy (1)",
    "creativity & inner joy (2)",
    "skill & learning through use",
    "beauty & insight",
    "balance & clarity",
    "expansion & vision",
    "devotion & good influence",
    "precision & refinement",
    "roots & breakthrough",
    "discipline & sustained effort",
    "strength & steady growth",
    "listening & teaching",
    "wealth & skilled rebuilding",
    "stillness & visionary thinking",
    "release & deep compassion (1)",
    "release & deep compassion (2)",
    "completion & refined return",
]

NAKSHATRA_KEYWORDS_NL: list[str] = [
    "heling & nieuwe start",
    "voeding & volhouden",
    "zuivering & scherpe focus",
    "groei & aantrekkingskracht",
    "zoeken & zachte nieuwsgierigheid",
    "verandering & ontwaken",
    "terugkeer & hernieuwde hoop",
    "steun & voeding",
    "verbinding & diepe intuïtie",
    "gezag & plezier in meesterschap",
    "creativiteit & innerlijke vreugde (1)",
    "creativiteit & innerlijke vreugde (2)",
    "vaardigheid & leren door doen",
    "schoonheid & inzicht",
    "balans & helderheid",
    "expansie & visie",
    "devotie & goede invloed",
    "precisie & verfijning",
    "wortels & doorbraak",
    "discipline & doorzettingskracht",
    "kracht & gestage groei",
    "luisteren & onderwijzen",
    "rijkdom & vaardig herstellen",
    "stilte & visionair denken",
    "loslaten & diepe compassie (1)",
    "loslaten & diepe compassie (2)",
    "afronding & verfijnde terugkeer",
]

NAKSHATRA_MEANINGS: dict[int, dict[Lang, str]] = {}
for idx in range(1, 28):
    name = NAKSHATRA_NAMES_EN[idx - 1]
    kw_en = NAKSHATRA_KEYWORDS_EN[idx - 1]
    kw_nl = NAKSHATRA_KEYWORDS_NL[idx - 1]
    NAKSHATRA_MEANINGS[idx] = {
        "nl": f"Nakshatra {idx} ({name}): {kw_nl}. Dit is de 'lading' van je geboortemoment op emotioneel en intuitief niveau.",
        "en": f"Nakshatra {idx} ({name}): {kw_en}. This is the emotional/intuitional charge of your birth moment.",
    }


# Yoga 1..27 (baseline generic)
YOGA_MEANINGS: dict[int, dict[Lang, str]] = {}
for _i in range(1, 28):
    if _i <= 9:
        nl = f"Yoga {_i}: Sun en Moon combineren in een toon van harmonie-je voelt makkelijker 'flow' en voelt waar je kunt meebewegen."
        en = f"Yoga {_i}: the Sun and Moon combine with a harmonic tone-you feel an easier flow and where to move with it."
    elif _i <= 18:
        nl = f"Yoga {_i}: Sun en Moon mengen in leerzame dynamiek-je groeit door afstemming, ritme en keuzes bij te stellen."
        en = f"Yoga {_i}: Sun and Moon mix into a learning dynamic-you grow through adjustment, pacing, and refined choices."
    else:
        nl = f"Yoga {_i}: Sun en Moon roepen transformatie op-waar je balans herstelt, verschijnt nieuwe richting."
        en = f"Yoga {_i}: Sun and Moon call for transformation-new direction appears when you restore balance."
    YOGA_MEANINGS[_i] = {"nl": nl, "en": en}


def aspect_meaning(locale: Optional[str], aspect_type: str, *, applying: Optional[bool] = None) -> str:
    lang = normalize_locale(locale)
    base = ASPECT_MEANINGS.get(aspect_type, {}).get(lang)
    if not base:
        base = {"nl": f"Aspect {aspect_type} vraagt aandacht voor de manier waarop twee krachten samenwerken.", "en": f"Aspect {aspect_type} asks for attention to how two forces collaborate."}[lang]
    if applying is None:
        return base
    if lang == "nl":
        if applying:
            return base + " Dit signaleert een 'aanwezige beweging' richting de exacte hoek (applicerend)."
        return base + " Dit signaleert een 'wegbeweging' van de exacte hoek (separerend)."
    if applying:
        return base + " This signals momentum toward the exact angle (applying)."
    return base + " This signals a movement away from the exact angle (separating)."


def house_meaning(locale: Optional[str], house_number: Optional[int]) -> str:
    lang = normalize_locale(locale)
    if house_number is None:
        return {"nl": "Huis-interpretatie niet beschikbaar.", "en": "House interpretation not available."}[lang]
    return HOUSE_MEANINGS.get(int(house_number), {}).get(lang, str(house_number))


def planet_meaning(locale: Optional[str], planet: Optional[str]) -> str:
    lang = normalize_locale(locale)
    if not planet:
        return {"nl": "Planeetinterpretatie niet beschikbaar.", "en": "Planet interpretation not available."}[lang]
    return PLANET_MEANINGS.get(planet, {}).get(lang, planet)


def stem_meaning(locale: Optional[str], stem: Optional[str]) -> str:
    lang = normalize_locale(locale)
    if not stem:
        return {"nl": "Steminterpretatie niet beschikbaar.", "en": "Stem interpretation not available."}[lang]
    return CHINESE_STEM_MEANINGS.get(stem, {}).get(lang, stem)


def branch_meaning(locale: Optional[str], branch: Optional[str]) -> str:
    lang = normalize_locale(locale)
    if not branch:
        return {"nl": "Branchinterpretatie niet beschikbaar.", "en": "Branch interpretation not available."}[lang]
    return CHINESE_BRANCH_MEANINGS.get(branch, {}).get(lang, branch)


def pillar_meaning(locale: Optional[str], *, pillar_kind: str, stem: str, branch: str) -> str:
    lang = normalize_locale(locale)
    pillar_label = {
        "year": {"nl": "Jaarpilaar", "en": "Year pillar"},
        "month": {"nl": "Maandpilaar", "en": "Month pillar"},
        "day": {"nl": "Dagpilaar", "en": "Day pillar"},
        "hour": {"nl": "Uurpilaar", "en": "Hour pillar"},
    }.get(pillar_kind, {"nl": pillar_kind, "en": pillar_kind})[lang]
    return chinese_pillar_meaning(lang, pillar_label=pillar_label, stem=stem, branch=branch)


def vaara_meaning(locale: Optional[str], vaara: Optional[str]) -> str:
    lang = normalize_locale(locale)
    if not vaara:
        return {"nl": "Vaara-interpretatie niet beschikbaar.", "en": "Vaara interpretation not available."}[lang]
    base = VAARA_MEANINGS.get(vaara, {}).get(lang, vaara)
    if lang == "nl":
        return base + " Gebruik het als een dagkleur: stem je agenda en je communicatie af op wat vandaag makkelijker 'ja' zegt."
    return base + " Use it as a daily color: align your actions and communication with what today naturally says 'yes' to."


def tithi_meaning(locale: Optional[str], tithi_index: Optional[int]) -> str:
    lang = normalize_locale(locale)
    if tithi_index is None:
        return {"nl": "Tithi-interpretatie niet beschikbaar.", "en": "Tithi interpretation not available."}[lang]
    idx = int(tithi_index)
    base = TITHI_MEANINGS.get(idx, {}).get(lang, str(idx))
    if lang == "nl":
        if idx <= 10:
            return base + " Deze fase helpt je om intentie om te zetten in concrete stappen, maar houdt je tempo best haalbaar."
        if idx <= 20:
            return base + " Hier werkt het goed om te doseren: kijk waar je informatie en emotie samenkomen, en kies dan gericht."
        return base + " Gebruik de fase om af te ronden met helderheid: laat los wat af is en maak ruimte voor het volgende."
    if idx <= 10:
        return base + " This phase supports turning intent into concrete steps, while keeping your pace realistic."
    if idx <= 20:
        return base + " Here it helps to pace yourself: notice where information and emotion meet, then choose deliberately."
    return base + " Use this phase to close with clarity: release what is complete and make room for what comes next."


def nakshatra_meaning(locale: Optional[str], nakshatra_index: Optional[int]) -> str:
    lang = normalize_locale(locale)
    if nakshatra_index is None:
        return {"nl": "Nakshatra-interpretatie niet beschikbaar.", "en": "Nakshatra interpretation not available."}[lang]
    idx = int(nakshatra_index)
    base = NAKSHATRA_MEANINGS.get(idx, {}).get(lang, str(idx))
    if lang == "nl":
        return base + " Door bewust te luisteren naar je innerlijke signalen kun je dit veld benutten voor betere keuzes en meer emotionele afstemming."
    return base + " By consciously listening to your inner signals, you can use this field for better choices and smoother emotional alignment."


def yoga_meaning(locale: Optional[str], yoga_index: Optional[int]) -> str:
    lang = normalize_locale(locale)
    if yoga_index is None:
        return {"nl": "Yoga-interpretatie niet beschikbaar.", "en": "Yoga interpretation not available."}[lang]
    idx = int(yoga_index)
    base = YOGA_MEANINGS.get(idx, {}).get(lang, str(idx))
    if lang == "nl":
        return base + " Het is nuttig om te kijken naar 'wat samenkomt': kies activiteiten waar energie van beide kanten in dezelfde richting werkt."
    return base + " It helps to look for what 'comes together': choose activities where energy from both sides points in the same direction."


# Chinese solar terms: indices 1..24 (jieqi)
SOLAR_TERM_MEANINGS: dict[int, dict[Lang, str]] = {
    1: {"nl": "Lichun: start van de lente-kwaliteit; nieuwe groei kan voorzichtig beginnen.", "en": "Lichun: the start of the spring quality; new growth can cautiously begin."},
    2: {"nl": "Yushui: de focus verschuift naar verzachting, voeding en 'in leven komen'.", "en": "Yushui: focus shifts to softening, nourishment, and coming alive."},
    3: {"nl": "Jingzhe: energie-ontwaken; acties krijgen momentum.", "en": "Jingzhe: awakening of energy; actions gain momentum."},
    4: {"nl": "Chunfen: lentebalans; iets rijpt, iets komt tot rust.", "en": "Chunfen: spring balance; something matures, something rests."},
    5: {"nl": "Qingming: helderheid en reiniging; plannen kunnen scherper.", "en": "Qingming: clarity and cleansing; plans can get sharper."},
    6: {"nl": "Guyu: groei met warmte; beweging wordt vruchtbaar.", "en": "Guyu: growth with warmth; motion becomes fruitful."},
    7: {"nl": "Lixia: begin van de zomer; energie wordt actiever en zichtbaarder.", "en": "Lixia: start of summer; energy becomes more active and visible."},
    8: {"nl": "Xiaoman: bijna-vol gevoel; verfijning en afronding van stappen.", "en": "Xiaoman: almost-full feeling; refine and complete steps."},
    9: {"nl": "Mangzhong: rijping; oogst-energie en verantwoordelijkheid.", "en": "Mangzhong: ripening; harvest energy and responsibility."},
    10: {"nl": "Xiazhi: zomerse piek; energiestroom is maximaal en vraagt richting.", "en": "Xiazhi: summer peak; energy flow is at its strongest and asks for direction."},
    11: {"nl": "Xiaoshu: warmte blijft; bouw ritme en uithouding.", "en": "Xiaoshu: warmth continues; build rhythm and endurance."},
    12: {"nl": "Dashu: grote warmte; focus op stabiliteit en energiehuishouding.", "en": "Dashu: great heat; focus on stability and energy management."},
    13: {"nl": "Liqiu: begin van de herfst; loslaten en heroriënteren.", "en": "Liqiu: start of autumn; letting go and reorienting."},
    14: {"nl": "Chushu: koelte komt; je aanpak kan gestructureerder worden.", "en": "Chushu: coolness arrives; your approach can become more structured."},
    15: {"nl": "Bailu: wit-dauw kwaliteit; verfijning, eerlijkheid en zuivering.", "en": "Bailu: dew/clarity quality; refinement, honesty, and purification."},
    16: {"nl": "Qiufen: herfstbalans; nuance en afstemming maken verschil.", "en": "Qiufen: autumn balance; nuance and alignment matter."},
    17: {"nl": "Hanlu: koeler en dieper; je innerlijke systeem krijgt aandacht.", "en": "Hanlu: cooler and deeper; your inner system gets attention."},
    18: {"nl": "Shuangjiang: overgang naar kou; voorbereiding en beheer van energie.", "en": "Shuangjiang: transition toward cold; prepare and manage energy."},
    19: {"nl": "Lidong: begin van de winter; bescherming, rust en herstel.", "en": "Lidong: start of winter; protection, rest, and recovery."},
    20: {"nl": "Xiaoxue: lichte sneeuw; langzaam intrekken en ordenen.", "en": "Xiaoxue: light snow; inward movement and ordering."},
    21: {"nl": "Daxue: meer sneeuw; grenzen voelen scherper en vragen discipline.", "en": "Daxue: more snow; boundaries sharpen and ask for discipline."},
    22: {"nl": "Dongzhi: winterzonnewende; herstartpunt in de cyclus.", "en": "Dongzhi: winter solstice; cycle restart point."},
    23: {"nl": "Xiaohan: verdere kou; consolideren en zacht blijven.", "en": "Xiaohan: further cold; consolidate and stay gentle."},
    24: {"nl": "Dahan: grote kou; afronden, vooruitplannen voor later, warmte binnenin.", "en": "Dahan: great cold; closure, planning for later, warmth within."},
}


def sign_meaning(locale: Optional[str], sign_code: Optional[str]) -> str:
    lang = normalize_locale(locale)
    if not sign_code:
        return {"nl": "Teken-interpretatie niet beschikbaar.", "en": "Sign interpretation not available."}[lang]
    return SIGN_MEANINGS.get(sign_code, {}).get(lang, sign_code)


def karana_meaning(locale: Optional[str], karana_index: Optional[int]) -> str:
    lang = normalize_locale(locale)
    if karana_index is None:
        return {"nl": "Karana-interpretatie niet beschikbaar.", "en": "Karana interpretation not available."}[lang]
    idx = int(karana_index)
    base = KARANA_MEANINGS.get(idx, {}).get(lang, str(idx))
    if lang == "nl":
        return base + " Denk eraan als een overgangsmechaniek: je profiteert het meest wanneer je bewust schakelt in plaats van achteraf te reageren."
    return base + " Treat it like a transition mechanism: you benefit most when you switch consciously rather than reacting after the fact."


def solar_term_meaning(locale: Optional[str], solar_term_index: Optional[int]) -> str:
    lang = normalize_locale(locale)
    if solar_term_index is None:
        return {"nl": "Solar-term interpretatie niet beschikbaar.", "en": "Solar term interpretation not available."}[lang]
    idx = int(solar_term_index)
    base = SOLAR_TERM_MEANINGS.get(idx, {}).get(lang, str(idx))
    if lang == "nl":
        return base + " Het helpt om dit te gebruiken als seizoenskompas: stuur je ritme en plannen mee met de veranderende kwaliteit van het klimaat."
    return base + " Use it as a seasonal compass: steer your rhythm and plans with the changing climate quality."

