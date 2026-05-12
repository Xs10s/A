"""Western tropical: factual headlines + sign/house-tuned personal layers."""

from __future__ import annotations

from typing import Any, Optional

from ..interpretations import _extended_aspect_paragraph, _extended_planet_paragraph, _sign_from_lon_deg
from ..knowledgebase import normalize_locale
from .types import ExplanationBlock, MethodExplanationBundle

_RULER_BY_SIGN: dict[str, str] = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Pluto",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Uranus", "Pisces": "Neptune",
}

_SUN_PERSONAL: dict[str, dict[str, str]] = {
    "Aries": {
        "nl": "Persoonlijk merk je dit vaak als een drang om te starten voordat alles perfect is. Groei zit in eerlijk proberen en bijsturen, niet in eeuwig wachten.",
        "en": "Personally you often feel a push to start before everything is perfect. Growth lives in honest trying and adjusting, not endless waiting.",
    },
    "Taurus": {
        "nl": "Persoonlijk zoek je rust als je iets tastbaars opbouwt: afspraken, lichaam, waarden. Je wordt onrustig als alles voortdurend moet veranderen zonder houvast.",
        "en": "Personally you settle when you build something tangible: agreements, body, values. You fray when everything must change without anchors.",
    },
    "Gemini": {
        "nl": "Persoonlijk heb je woorden, ideeen en afwisseling nodig om jezelf te begrijpen. Als je moet 'kiezen voor altijd' voelt dat snel benauwend.",
        "en": "Personally you need words, ideas, and variety to understand yourself. 'Choose forever' can feel suffocating quickly.",
    },
    "Cancer": {
        "nl": "Persoonlijk vraagt je kern om veiligheid en trouw. Je groeit als je grenzen mag stellen zonder je zorgzaamheid te verliezen.",
        "en": "Personally your core asks for safety and loyalty. You grow when you can set boundaries without losing your care.",
    },
    "Leo": {
        "nl": "Persoonlijk wil je gezien worden in wat echt van jou is: niet als show, maar als warmte. Erkenning voedt je; koude of negeren raakt diep.",
        "en": "Personally you want to be seen in what is truly yours: not performance, but warmth. Recognition feeds you; coldness cuts deep.",
    },
    "Virgo": {
        "nl": "Persoonlijk kalmeer je door nuttig te zijn en dingen te verbeteren. Let op schuldgevoel: je waarde is niet gelijk aan je productiviteit.",
        "en": "Personally you calm through usefulness and refinement. Watch guilt: your worth is not your productivity.",
    },
    "Libra": {
        "nl": "Persoonlijk leer je via relaties en tegenstellingen. Je groei is om eerlijk te kiezen zonder jezelf weg te stemmen.",
        "en": "Personally you learn through relationships and contrast. Growth is honest choosing without erasing yourself.",
    },
    "Scorpio": {
        "nl": "Persoonlijk wil je diepte en waarheid; oppervlakkigheid voelt leeg. Vertrouwen bouw je met transparantie en tijd, niet met forceren.",
        "en": "Personally you want depth and truth; surface feels empty. Trust builds with transparency and time, not force.",
    },
    "Sagittarius": {
        "nl": "Persoonlijk heb je zin en bewegingsruimte nodig. Je wordt somber als alles klein en star wordt; hoop en leren geven weer lucht.",
        "en": "Personally you need meaning and room to move. You dim when life feels small and rigid; hope and learning reopen space.",
    },
    "Capricorn": {
        "nl": "Persoonlijk neem je verantwoordelijkheid serieus, soms te serieus. Groei is ambitie koppelen aan rust en menselijkheid.",
        "en": "Personally you take responsibility seriously, sometimes too seriously. Growth links ambition with rest and humanity.",
    },
    "Aquarius": {
        "nl": "Persoonlijk wil je vrijheid en rechtvaardigheid. Je bloeit als 'anders' een bijdrage mag zijn, geen bewijsstuk.",
        "en": "Personally you want freedom and fairness. You bloom when difference is contribution, not proof.",
    },
    "Pisces": {
        "nl": "Persoonlijk neem je de sfeer mee; grenzen zijn dan geen luxe. Zachtheid werkt het best met heldere ja/nee.",
        "en": "Personally you absorb atmosphere; boundaries are not luxury. Softness works best with clear yes/no.",
    },
}

_MOON_PERSONAL: dict[str, dict[str, str]] = {
    "Aries": {
        "nl": "Persoonlijk verwerk je gevoel snel als je het mag uiten: beweging, directheid, actie. Onderdrukte boosheid wordt snel innerlijke ruis.",
        "en": "Personally you process feeling when you can move it: motion, directness, action. Suppressed anger becomes inner noise fast.",
    },
    "Taurus": {
        "nl": "Persoonlijk heb je voorspelbaarheid en zintuiglijke rust nodig. Grote schokken of haast voelen onveilig aan, ook als anderen ze normaal vinden.",
        "en": "Personally you need predictability and sensory calm. Shock or hurry can feel unsafe even if others call it normal.",
    },
    "Gemini": {
        "nl": "Persoonlijk orden je emoties door te praten, te schrijven of nieuwe info. Stilstand voelt sneller bedreigend dan rust.",
        "en": "Personally you sort emotions by talking, writing, or new input. Stillness can feel more threatening than restful.",
    },
    "Cancer": {
        "nl": "Persoonlijk is 'thuis' je laadpunt: mensen of plekken. Je neemt stemmingen mee; check daarom regelmatig wat van jou is.",
        "en": "Personally 'home' is your charger: people or places. You pick up moods; check often what is yours.",
    },
    "Leo": {
        "nl": "Persoonlijk heb je warme bevestiging nodig om je veilig te voelen. Kritiek kan hard binnenkomen, ook als die goed bedoeld is.",
        "en": "Personally warm affirmation helps you feel safe. Critique can land hard even when well meant.",
    },
    "Virgo": {
        "nl": "Persoonlijk kalmeer je door grip: opruimen, verbeteren, zorg dragen. Zelfcompassie is een vaardigheid om te oefenen, geen luxe.",
        "en": "Personally you calm through grip: tidy, improve, care. Self-compassion is a skill to practice, not a luxury.",
    },
    "Libra": {
        "nl": "Persoonlijk zoek je harmonie, maar spanning in relaties voel je lichamelijk. Oefen met kiezen wat jij wilt, niet alleen wat eerlijk verdeeld lijkt.",
        "en": "Personally you seek harmony, but relationship tension hits your body. Practice choosing what you want, not only what looks fair.",
    },
    "Scorpio": {
        "nl": "Persoonlijk ga je onder water pas open als er vertrouwen is. Diepgang is voeding; kleine praat kan uitputten als het maskers zijn.",
        "en": "Personally you open underwater only with trust. Depth feeds you; small talk drains when it masks.",
    },
    "Sagittarius": {
        "nl": "Persoonlijk heb je perspectief nodig: humor, betekenis, ruimte. Als alles moet passen in een kader, voel je je snel ingesloten.",
        "en": "Personally you need perspective: humor, meaning, space. One tight frame can feel like a cage quickly.",
    },
    "Capricorn": {
        "nl": "Persoonlijk houd je gevoel strak tot het veilig is. Dat kan stoer lijken; van binnen vraag je vaak of je mag rusten zonder te falen.",
        "en": "Personally you hold feeling tight until it is safe. It can look stoic; inside you often ask if you may rest without failing.",
    },
    "Aquarius": {
        "nl": "Persoonlijk orden je emoties ook rationeel: principes, vriendschap, 'waarom zo?'. Afstand helpt, alleen niet te lang, dan wordt het koud.",
        "en": "Personally you sort emotions rationally too: principles, friendship, 'why so?'. Distance helps, not so long it turns cold.",
    },
    "Pisces": {
        "nl": "Persoonlijk absorbeer je de sfeer; muziek, stilte of water helpt filteren. Grenzen zijn bescherming, geen afwijzing van anderen.",
        "en": "Personally you absorb atmosphere; music, silence, or water filters. Boundaries are protection, not rejection of others.",
    },
}

_ASC_PERSONAL: dict[str, dict[str, str]] = {
    "Aries": {
        "nl": "Persoonlijk merken mensen snel je tempo en durf; je leert om impuls niet te verwarren met onverschilligheid.",
        "en": "Personally people notice your pace and nerve; you learn impulse is not indifference.",
    },
    "Taurus": {
        "nl": "Persoonlijk maak je een kalme, betrouwbare eerste indruk; vertrouwen groeit als je consequent blijft.",
        "en": "Personally you read calm and reliable; trust grows when you stay consistent.",
    },
    "Gemini": {
        "nl": "Persoonlijk kom je licht en nieuwsgierig over; soms denken mensen dat je oppervlakkig bent terwijl je vooral veel parallel ziet.",
        "en": "Personally you land light and curious; people may read depth as scatter when you simply see parallel tracks.",
    },
    "Cancer": {
        "nl": "Persoonlijk voelen anderen warmte of voorzichtigheid eerst; je gevoel voor de kamer is sterk.",
        "en": "Personally others feel warmth or caution first; your read of the room is strong.",
    },
    "Leo": {
        "nl": "Persoonlijk val je op door stijl of hart; je oefening is warmte delen zonder voortdurend bewijs te leveren.",
        "en": "Personally you stand out with style or heart; the practice is warmth without constant proving.",
    },
    "Virgo": {
        "nl": "Persoonlijk oog je ingetogen en precies; mensen missen soms je zachte kant achter de zorg voor details.",
        "en": "Personally you read contained and precise; people can miss your softness behind the detail care.",
    },
    "Libra": {
        "nl": "Persoonlijk zoek je meteen naar sfeer en eerlijkheid; conflict voelt snel lichamelijk.",
        "en": "Personally you scan for tone and fairness fast; conflict lands in your body quickly.",
    },
    "Scorpio": {
        "nl": "Persoonlijk straal je intensiteit of reserve uit; vertrouwen win je met tijd, niet met een grotere glimlach.",
        "en": "Personally you radiate intensity or reserve; trust comes with time, not bigger smiles.",
    },
    "Sagittarius": {
        "nl": "Persoonlijk kom je open en zoekend over; je eerste stap is vaak ruimte maken voor mogelijkheden.",
        "en": "Personally you read open and seeking; your first step often widens the field of possibilities.",
    },
    "Capricorn": {
        "nl": "Persoonlijk oog je serieuzer dan je soms voelt; je ordent eerst, daarna komt gevoel.",
        "en": "Personally you read more serious than you sometimes feel; you sort first, feel after.",
    },
    "Aquarius": {
        "nl": "Persoonlijk val je op door eigen koers; distantie is vaak observatie, geen desinteresse.",
        "en": "Personally you stand out with your own course; distance is often observation, not disinterest.",
    },
    "Pisces": {
        "nl": "Persoonlijk voelen mensen zachtheid of openheid; jouw werk is zachtheid met duidelijke grenzen te paren.",
        "en": "Personally people feel softness or openness; your work is pairing softness with clear edges.",
    },
}


def _pick(table: dict[str, dict[str, str]], sign: Optional[str], lang: str) -> str:
    if not sign:
        return ""
    row = table.get(sign) or {}
    return str(row.get(lang) or row.get("en") or "")


def _top_aspect_lines(aspects: list[dict[str, Any]], *, locale: str, limit: int = 2) -> list[str]:
    rows: list[tuple[float, dict[str, Any]]] = []
    for a in aspects:
        if not isinstance(a, dict):
            continue
        try:
            orb = a.get("orb_deg") if a.get("orb_deg") is not None else a.get("orb_degrees")
            orb_f = float(orb) if orb is not None else 999.0
        except Exception:
            orb_f = 999.0
        rows.append((orb_f, a))
    rows.sort(key=lambda x: x[0])
    out: list[str] = []
    for _, a in rows[:limit]:
        out.append(
            _extended_aspect_paragraph(
                locale,
                a=str(a.get("a") or ""),
                b=str(a.get("b") or ""),
                aspect_type=str(a.get("type") or ""),
                applying=bool(a.get("applying", False)),
                orb_deg=a.get("orb_deg") if a.get("orb_deg") is not None else a.get("orb_degrees"),
            )
        )
    return out


def build_western_tropical_bundle(engine_json: dict[str, Any], *, locale: str) -> MethodExplanationBundle:
    lang = normalize_locale(locale)
    western = engine_json.get("western") if isinstance(engine_json.get("western"), dict) else {}
    placements = western.get("placements") if isinstance(western.get("placements"), dict) else {}
    aspects = western.get("aspects") if isinstance(western.get("aspects"), list) else []
    houses = western.get("houses") if isinstance(western.get("houses"), dict) else {}
    angles = houses.get("angles") if isinstance(houses.get("angles"), dict) else {}
    asc_deg = angles.get("asc_deg")

    blocks: list[ExplanationBlock] = []

    sun = placements.get("Sun") if isinstance(placements.get("Sun"), dict) else {}
    moon = placements.get("Moon") if isinstance(placements.get("Moon"), dict) else {}
    sun_sign = sun.get("sign") if isinstance(sun.get("sign"), str) else None
    moon_sign = moon.get("sign") if isinstance(moon.get("sign"), str) else None
    sun_house = sun.get("house")
    moon_house = moon.get("house")

    if sun_sign:
        headline = _extended_planet_paragraph(
            locale, planet="Sun", sign=sun_sign, house=int(sun_house) if isinstance(sun_house, int) else None
        )
        blocks.append(
            {
                "id": "sun",
                "title": "Zon" if lang == "nl" else "Sun",
                "headline": headline,
                "personal_layer": _pick(_SUN_PERSONAL, sun_sign, lang),
                "reflection_questions": [
                    "Waar merk je dit weekritme het sterkst in je agenda?"
                    if lang == "nl"
                    else "Where do you notice this rhythm strongest in your week?",
                ],
            }
        )

    if moon_sign:
        headline = _extended_planet_paragraph(
            locale, planet="Moon", sign=moon_sign, house=int(moon_house) if isinstance(moon_house, int) else None
        )
        blocks.append(
            {
                "id": "moon",
                "title": "Maan" if lang == "nl" else "Moon",
                "headline": headline,
                "personal_layer": _pick(_MOON_PERSONAL, moon_sign, lang),
                "reflection_questions": [
                    "Wat is je meest betrouwbare manier om weer tot rust te komen?"
                    if lang == "nl"
                    else "What is your most reliable way to return to calm?",
                ],
            }
        )

    asc_sign: Optional[str] = None
    if isinstance(asc_deg, (int, float)):
        asc_sign = _sign_from_lon_deg(float(asc_deg))
        headline = _extended_planet_paragraph(locale, planet="Asc", sign=asc_sign, house=1)
        ruler = _RULER_BY_SIGN.get(asc_sign or "")
        ruler_pl = placements.get(ruler) if ruler and isinstance(placements.get(ruler), dict) else {}
        ruler_sign = ruler_pl.get("sign") if isinstance(ruler_pl.get("sign"), str) else None
        extra = ""
        if ruler and ruler_sign:
            if lang == "nl":
                extra = f" Je chart ruler ({ruler}) staat in {ruler_sign}; dat kleurt hoe je eerste indruk in de praktijk werkt."
            else:
                extra = f" Your chart ruler ({ruler}) sits in {ruler_sign}; that tints how your first impression plays out."
        blocks.append(
            {
                "id": "ascendant",
                "title": "Ascendant",
                "headline": headline,
                "personal_layer": _pick(_ASC_PERSONAL, asc_sign, lang) + extra,
                "reflection_questions": [
                    "Hoe gedraag je je automatisch in een nieuwe groep?"
                    if lang == "nl"
                    else "How do you automatically behave in a new group?",
                ],
            }
        )

    for line in _top_aspect_lines(aspects, locale=locale, limit=2):
        blocks.append(
            {
                "id": f"aspect_{len(blocks)}",
                "title": "Aspect" if lang == "nl" else "Aspect",
                "headline": line,
                "personal_layer": (
                    "Persoonlijk: merk op wanneer dit thema samen met stress, energie of relaties optelt; dat is je oefenterrein."
                    if lang == "nl"
                    else "Personally: notice when this theme stacks with stress, energy, or relationships; that is your practice field."
                ),
            }
        )

    if not blocks:
        blocks.append(
            {
                "id": "empty",
                "title": "Westers (tropisch)",
                "headline": (
                    "Nog geen Westerse plaatsingen beschikbaar voor deze berekening."
                    if lang == "nl"
                    else "No Western placements available for this calculation yet."
                ),
                "personal_layer": (
                    "Persoonlijk: zodra datum, tijd (voor huizen) en locatie kloppen, vullen Zon, Maan en Ascendant zich hier."
                    if lang == "nl"
                    else "Personally: once date, time (for houses), and location are solid, Sun, Moon, and Ascendant fill in here.",
                ),
            }
        )

    overview = (
        "Westerse uitleg: eerst de feitelijke plaatsing, daarna wat dit vaak persoonlijk raakt. Geen voorspelling, wel herkenning."
        if lang == "nl"
        else "Western reading: factual placement first, then what it often touches personally. Not a forecast, recognition."
    )
    closing = (
        "Combineer deze blokken met je radix en tabellen; zo wordt de formule een verhaal dat bij jouw leven past."
        if lang == "nl"
        else "Read these blocks alongside your wheel and tables so the formula becomes a story that fits your life."
    )

    return {
        "method_id": "western_tropical",
        "locale": locale,
        "version": "1.0.0",
        "overview": overview,
        "blocks": blocks,
        "closing_note": closing,
    }
