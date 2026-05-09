"""
Unified Energy Profile "book" generator.

Builds one cross-method profile structure meant for the Energieprofiel tab:
- personal introduction
- core summary (long-form, deterministic)
- themes, balances, timing, tensions, growth
- compact per-method perspective cards

All text is computed from real engine-derived outputs:
energy profiles, cross-system resonance, and interpretation blocks.
"""

from __future__ import annotations

from typing import Any, Optional

from .knowledgebase import normalize_locale


def _L(locale: str, nl: str, en: str) -> str:
    return nl if normalize_locale(locale) == "nl" else en


def _get_profile(profiles: list[dict[str, Any]], system_id: str) -> Optional[dict[str, Any]]:
    for p in profiles:
        sid = ((p.get("system") or {}).get("id") if isinstance(p, dict) else None)
        if sid == system_id:
            return p
    return None


def _domain_by_key(profile: Optional[dict[str, Any]], key: str) -> Optional[dict[str, Any]]:
    if not isinstance(profile, dict):
        return None
    domains = profile.get("domains") or []
    if not isinstance(domains, list):
        return None
    for d in domains:
        if isinstance(d, dict) and d.get("key") == key:
            return d
    return None


def _top_domains(profile: Optional[dict[str, Any]], n: int = 3) -> list[dict[str, Any]]:
    if not isinstance(profile, dict):
        return []
    domains = [d for d in (profile.get("domains") or []) if isinstance(d, dict)]
    domains.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
    return domains[:n]


def _bottom_domains(profile: Optional[dict[str, Any]], n: int = 2) -> list[dict[str, Any]]:
    if not isinstance(profile, dict):
        return []
    domains = [d for d in (profile.get("domains") or []) if isinstance(d, dict)]
    domains.sort(key=lambda x: float(x.get("score", 0.0)))
    return domains[:n]


def _method_profiles(combined: dict[str, Any]) -> list[dict[str, Any]]:
    profiles = combined.get("profiles") if isinstance(combined, dict) else []
    if not isinstance(profiles, list):
        return []
    out: list[dict[str, Any]] = []
    for p in profiles:
        if not isinstance(p, dict):
            continue
        sid = ((p.get("system") or {}).get("id") if isinstance(p.get("system"), dict) else None) or ""
        domains = [d for d in (p.get("domains") or []) if isinstance(d, dict)]
        domains.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
        top = domains[:3]
        low = domains[-2:] if len(domains) >= 2 else domains[-1:]
        out.append(
            {
                "method": sid,
                "themes": [d.get("label") for d in top if d.get("label")],
                "elements": [],
                "polarities": [],
                "archetypes": [],
                "timing": [],
                "strengths": [d.get("label") for d in top if d.get("label")],
                "tensions": [d.get("label") for d in low if d.get("label")],
                "growthPatterns": [d.get("key") for d in low if d.get("key")],
                "relationshipPatterns": [],
                "energyFlow": [d.get("key") for d in top if d.get("key")],
                "narrativeFragments": [
                    str((p.get("narrative") or {}).get("summary") or "")
                ],
                "confidenceScore": round(
                    sum(float(d.get("score", 0.0)) for d in top) / max(1, len(top)), 1
                ),
            }
        )
    return out


def _average_domain_map(combined: dict[str, Any]) -> dict[str, float]:
    profiles = combined.get("profiles") if isinstance(combined, dict) else []
    if not isinstance(profiles, list):
        return {}
    acc: dict[str, list[float]] = {}
    for p in profiles:
        for d in (p.get("domains") or []):
            if not isinstance(d, dict):
                continue
            k = d.get("key")
            if not k:
                continue
            acc.setdefault(k, []).append(float(d.get("score", 0.0)))
    out: dict[str, float] = {}
    for k, vals in acc.items():
        out[k] = round(sum(vals) / max(1, len(vals)), 1)
    return out


def _theme_rows(
    locale: str,
    avg_domains: dict[str, float],
    combined: dict[str, Any],
    cross_system: dict[str, Any],
) -> list[dict[str, Any]]:
    profiles = combined.get("profiles") if isinstance(combined, dict) else []
    candidate = sorted(avg_domains.items(), key=lambda kv: kv[1], reverse=True)[:5]
    rows: list[dict[str, Any]] = []
    resonance = ((cross_system.get("convergence") or {}).get("element") if isinstance(cross_system, dict) else None)
    for key, score in candidate:
        supporting: list[str] = []
        for p in profiles:
            sid = ((p.get("system") or {}).get("id") if isinstance(p, dict) else None) or ""
            d = _domain_by_key(p, key)
            if d and float(d.get("score", 0.0)) >= 55.0:
                supporting.append(sid)
        title = _L(
            locale,
            f"Thema: {key}",
            f"Theme: {key}",
        )
        summary = _L(
            locale,
            f"Dit patroon komt terug in meerdere berekeningslagen met een gemiddelde intensiteit van {score}.",
            f"This pattern recurs across multiple computed layers with an average intensity of {score}.",
        )
        explanation = _L(
            locale,
            "In dagelijkse praktijk zie je dit vooral in hoe je keuzes maakt, energie verdeelt en reageert op ritmeverandering.",
            "In daily life this is most visible in how you make choices, distribute energy, and respond to rhythm shifts.",
        )
        if resonance:
            explanation += _L(
                locale,
                f" De elementresonantie ({resonance}) kleurt dit thema extra.",
                f" Element resonance ({resonance}) colors this theme further.",
            )
        rows.append(
            {
                "title": title,
                "summary": summary,
                "explanation": explanation,
                "daily_recognition": _L(
                    locale,
                    "Herkenbaar als terugkerend gedrag onder druk, in relaties en in werkritme.",
                    "Often recognizable as recurring behavior under pressure, in relationships, and in work rhythm.",
                ),
                "supported_by": supporting,
                "domain_key": key,
                "score": score,
            }
        )
    return rows[:5]


def _core_summary(
    locale: str,
    base_profile: Optional[dict[str, Any]],
    combined: dict[str, Any],
    cross_system: dict[str, Any],
) -> str:
    top = _top_domains(base_profile, 3)
    low = _bottom_domains(base_profile, 2)
    top_labels = ", ".join(str(d.get("label") or d.get("key")) for d in top) or _L(locale, "geen", "none")
    low_labels = ", ".join(str(d.get("label") or d.get("key")) for d in low) or _L(locale, "geen", "none")
    parity = (combined.get("parityNotes") or [None])[0] if isinstance(combined, dict) else None
    elem = ((cross_system.get("convergence") or {}).get("element") if isinstance(cross_system, dict) else None) or "-"
    pol = ((cross_system.get("convergence") or {}).get("polarity") if isinstance(cross_system, dict) else None) or "-"
    decision = None
    timing = None
    for s in (cross_system.get("sections") or []):
        if not isinstance(s, dict):
            continue
        if s.get("key") == "decision_resonance":
            decision = s.get("text")
        if s.get("key") == "timing_resonance":
            timing = s.get("text")

    if normalize_locale(locale) == "nl":
        paragraphs = [
            (
                "Je profiel laat patronen zien die niet uit een enkel systeem komen, maar uit een samenlezing van meerdere symbolische talen. "
                f"Wanneer we je gegevens door de verschillende modellen leggen, komen vooral {top_labels} naar voren als terugkerende dragers van je energie. "
                "Dat betekent niet dat deze thema's je volledig bepalen; het betekent dat ze in verschillende rekenkaders opnieuw zichtbaar worden, en daardoor betrouwbaarder zijn als observatiepunt."
            ),
            (
                f"Tegelijk laat je profiel ook ontwikkelruimte zien rond {low_labels}. "
                "Juist daar ontstaat vaak het verschil tussen potentie en draagkracht: je ziet wat je systeem al sterk organiseert, en waar ritme, herstel of begrenzing nog bewuster mogen worden opgebouwd. "
                "In deze lezing zijn zwakkere scores geen tekort, maar aanwijzingen voor waar je integratie nodig hebt."
            ),
            (
                f"Over systemen heen zien we elementaire convergentie rond {elem} en een polariteitsaccent rond {pol}. "
                "Dat geeft een bruikbare bril: niet als label, maar als werkhypothese voor je dagelijkse energiebeheer. "
                "Als meerdere methodes dezelfde richting markeren, is dat meestal een teken dat dit thema in verschillende levenscontexten opnieuw opduikt: in werkdruk, in relationele dynamiek, en in hoe je herstel organiseert."
            ),
            (
                (str(parity) + " ") if parity else ""
                + "Wanneer systemen verschillen, is dat geen fout in de berekening maar inhoudelijke nuance. "
                "Sommige modellen beschrijven je innerlijke beleving, andere je gedragsritme, weer andere je timing in langere cycli. "
                "De waarde zit in de overlap, maar ook in de afwijking: spanning tussen invalshoeken helpt om complexere patronen te zien die in een enkel model te plat zouden worden."
            ),
            (
                (decision + " ") if decision else ""
                + "In besluitvorming betekent dit profiel dat je beter functioneert wanneer keuzes niet alleen cognitief worden gemaakt, maar ook worden getoetst aan lichaamssignalen, emotionele timing en relationele context. "
                "Dat is geen vaag advies: het volgt uit de combinatie van je geobserveerde dominanten en de manier waarop verschillende systemen je flow en frictie beschrijven."
            ),
            (
                (timing + " ") if timing else ""
                + "Tijd werkt in dit profiel niet lineair maar cyclisch. "
                "Er zijn periodes waarin energie vanzelf samenvalt met richting, en periodes waarin dezelfde inspanning meer weerstand geeft. "
                "Door cycli bewust te lezen, verschuift de vraag van 'hoe forceer ik resultaat?' naar 'welk ritme ondersteunt nu het juiste type actie?'."
            ),
            (
                "De kern van dit Energieprofiel is daarom geen voorspelling, maar een integratiekader. "
                "Je ziet waar meerdere systemen elkaar versterken, waar ze elkaar corrigeren, en waar ze verschillende talen spreken over hetzelfde onderliggende patroon. "
                "Gebruik dit als persoonlijke ingang naar de methodetabbladen: niet om een absoluut antwoord te zoeken, maar om je eigen terugkerende dynamiek scherper en menselijker te begrijpen."
            ),
        ]
        return "\n\n".join(paragraphs)

    paragraphs_en = [
        (
            "Your profile reveals patterns that do not come from one system alone, but from a composite reading across symbolic languages. "
            f"When your data is processed through these models, {top_labels} repeatedly emerge as core energetic carriers. "
            "This does not mean these themes define you absolutely; it means they recur across computational frames and therefore become more dependable as observation points."
        ),
        (
            f"At the same time, the profile highlights developmental space around {low_labels}. "
            "This is often where potential and capacity diverge: you can see what your system already organizes well, and where rhythm, recovery, or boundaries need more deliberate construction. "
            "In this reading, lower scores are not deficits; they are integration signals."
        ),
        (
            f"Across systems we see elemental convergence around {elem} and polarity emphasis around {pol}. "
            "Treat this as a practical lens rather than an identity label. "
            "When several methods point in one direction, that usually marks a theme that reappears in multiple life contexts: workload, relational dynamics, and recovery design."
        ),
        (
            (str(parity) + " ") if parity else ""
            + "When systems diverge, that is not computational failure but interpretive nuance. "
            "Some models describe inner experience, others behavioral rhythm, others long-cycle timing. "
            "The value lies in overlap, but also in deviation: tension between perspectives reveals complexity that a single model would flatten."
        ),
        (
            (decision + " ") if decision else ""
            + "For decision-making, this profile suggests that choices work better when they are not purely cognitive, but tested against body feedback, emotional timing, and relational context. "
            "This is not generic advice; it follows directly from your computed dominant patterns and where systems align on flow versus friction."
        ),
        (
            (timing + " ") if timing else ""
            + "Timing in this profile is cyclical rather than linear. "
            "Some periods align energy and direction naturally, while others create resistance for the same effort. "
            "Reading cycles consciously shifts the question from 'how do I force output?' to 'which rhythm supports the right kind of action now?'."
        ),
        (
            "So this Energy Profile is not a prediction, but an integration framework. "
            "It shows where systems reinforce each other, where they correct each other, and where they describe the same pattern through different symbolic vocabularies. "
            "Use it as your entry point into the method tabs: not to find one absolute answer, but to understand recurring human dynamics in your own life with more precision."
        ),
    ]
    return "\n\n".join(paragraphs_en)


def build_profile_book(
    engine_json: dict[str, Any],
    *,
    combined_energy: dict[str, Any],
    cross_system: dict[str, Any],
    interpretations: dict[str, Any],
    locale: str = "nl-NL",
) -> dict[str, Any]:
    lang = normalize_locale(locale)
    profiles = combined_energy.get("profiles") if isinstance(combined_energy, dict) else []
    if not isinstance(profiles, list):
        profiles = []
    base = _get_profile(profiles, "western_tropical") or (profiles[0] if profiles else None)
    avg_domains = _average_domain_map(combined_energy)
    themes = _theme_rows(locale, avg_domains, combined_energy, cross_system)
    method_profiles = _method_profiles(combined_energy)

    core_summary = _core_summary(locale, base, combined_energy, cross_system)
    top = _top_domains(base, 3)
    low = _bottom_domains(base, 2)

    intro = _L(
        locale,
        "Dit profiel brengt meerdere astrologische talen samen in een leesbare synthese. Geen losse horoscopen, maar een samengesteld patroonbeeld op basis van jouw geboortedata.",
        "This profile combines multiple astrological languages into one readable synthesis. Not separate horoscopes, but one composite pattern map based on your birth data.",
    )

    perspectives = [
        {
            "method": "western_tropical",
            "title": _L(locale, "Westers", "Western"),
            "what_it_reads": _L(locale, "Psychologische dynamiek via planeten, tekens, huizen en aspecten.", "Psychological dynamics through planets, signs, houses, and aspects."),
            "personal_summary": str(((interpretations.get("western_tropical") or {}).get("summary") or "")),
            "key_finding": str(((_top_domains(_get_profile(profiles, "western_tropical"), 1) or [{}])[0].get("label") or "-")),
            "target_tab": "western",
        },
        {
            "method": "vedic_panchanga",
            "title": _L(locale, "Vedisch", "Vedic"),
            "what_it_reads": _L(locale, "Tijdskwaliteit en ritme van het moment via Panchanga.", "Moment quality and rhythm through Panchanga."),
            "personal_summary": str(((interpretations.get("vedic_panchanga") or {}).get("summary") or "")),
            "key_finding": str(((_top_domains(_get_profile(profiles, "vedic_panchanga"), 1) or [{}])[0].get("label") or "-")),
            "target_tab": "vedic",
        },
        {
            "method": "chinese_bazi",
            "title": "BaZi",
            "what_it_reads": _L(locale, "Cyclische patronen via stamen, takken en pijlers.", "Cyclical patterns via stems, branches, and pillars."),
            "personal_summary": str(((interpretations.get("chinese_ganzhi_bazi") or {}).get("summary") or "")),
            "key_finding": str(((_top_domains(_get_profile(profiles, "chinese_bazi"), 1) or [{}])[0].get("label") or "-")),
            "target_tab": "bazi",
        },
        {
            "method": "human_design",
            "title": "Human Design",
            "what_it_reads": _L(locale, "Besluitvorming en energiestroom via type, authoriteit en centra.", "Decision style and energy flow through type, authority, and centers."),
            "personal_summary": str(((interpretations.get("human_design") or {}).get("summary") or "")),
            "key_finding": str(((_top_domains(_get_profile(profiles, "human_design"), 1) or [{}])[0].get("label") or "-")),
            "target_tab": "humandesign",
        },
        {
            "method": "maya",
            "title": "Maya",
            "what_it_reads": _L(locale, "Ritme en tijdlaag via kin, toon en teken.", "Rhythm and time layer via kin, tone, and sign."),
            "personal_summary": str(((interpretations.get("maya") or {}).get("summary") or "")),
            "key_finding": str(((_top_domains(_get_profile(profiles, "maya"), 1) or [{}])[0].get("label") or "-")),
            "target_tab": "maya",
        },
    ]

    return {
        "intro": {
            "title": _L(locale, "Persoonlijke introductie", "Personal introduction"),
            "text": intro,
        },
        "core_summary": {
            "title": _L(locale, "Kernsamenvatting", "Core summary"),
            "text": core_summary,
            "word_count": len(core_summary.split()),
        },
        "main_themes": themes,
        "energetic_balance": {
            "average_domains": avg_domains,
            "element_convergence": (cross_system.get("convergence") or {}).get("element"),
            "polarity_convergence": (cross_system.get("convergence") or {}).get("polarity"),
            "top_domains": top,
            "low_domains": low,
        },
        "decision_flow": next(
            (s for s in (cross_system.get("sections") or []) if isinstance(s, dict) and s.get("key") == "decision_resonance"),
            {},
        ),
        "timing_cycles": next(
            (s for s in (cross_system.get("sections") or []) if isinstance(s, dict) and s.get("key") == "timing_resonance"),
            {},
        ),
        "tensions_contrasts": {
            "text": _L(
                locale,
                "Spanningen in dit profiel ontstaan waar sterke domeinen en ontwikkeldomeinen tegelijk actief zijn. Dat is geen contradictie maar een ontwikkelas.",
                "Tensions in this profile arise where strong domains and developmental domains are active at the same time. This is not contradiction but growth axis.",
            ),
            "strongest": top,
            "weakest": low,
        },
        "growth_integration": {
            "text": _L(
                locale,
                "Integratie ontstaat door je sterkste patronen bewust in te zetten ten dienste van je minst stabiele lagen.",
                "Integration emerges when your strongest patterns are consciously used in service of your least stable layers.",
            )
        },
        "method_perspectives": perspectives,
        "deep_dive_navigation": [
            {"target_tab": "western", "label": _L(locale, "Ga naar Westers", "Go to Western")},
            {"target_tab": "vedic", "label": _L(locale, "Ga naar Vedisch", "Go to Vedic")},
            {"target_tab": "bazi", "label": _L(locale, "Ga naar BaZi", "Go to BaZi")},
            {"target_tab": "humandesign", "label": _L(locale, "Ga naar Human Design", "Go to Human Design")},
            {"target_tab": "maya", "label": _L(locale, "Ga naar Maya", "Go to Maya")},
        ],
        "method_profiles": method_profiles,
        "meta": {
            "language": lang,
            "source": "cross-system-profile-book-v1",
            "sections": [
                "intro",
                "core_summary",
                "main_themes",
                "energetic_balance",
                "decision_flow",
                "timing_cycles",
                "tensions_contrasts",
                "growth_integration",
                "method_perspectives",
                "deep_dive_navigation",
            ],
        },
    }

