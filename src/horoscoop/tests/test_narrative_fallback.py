from __future__ import annotations

from horoscoop.interpretation.types import InterpretationPoint
from horoscoop.narrative import (
    build_fallback_narrative,
    generate_narrative,
    render_point_fallback,
)


def _point(method: str = "western", section: str = "core_identity") -> InterpretationPoint:
    return {
        "formulaId": "western.planet_in_sign_in_house",
        "method": method,
        "section": section,
        "technicalLabel": "Sun in Sagittarius (huis 9)",
        "humanMeaning": "bewuste levensenergie wordt gekleurd door zoeken naar betekenis",
        "balancedExpression": "in balans uitnodigend",
        "shadowExpression": "uit balans rusteloos",
        "reflectionQuestions": ["Waar zoek ik betekenis?"],
        "glossarySources": ["western.planet.sun", "western.sign.sagittarius", "western.house.9"],
        "inputs": {"planet": "sun", "sign": "Sagittarius", "house": "9"},
        "confidence": "high",
        "relationshipType": "expression_in_life_area",
    }


def test_render_point_fallback_includes_label_and_meaning():
    text = render_point_fallback(_point())
    assert "Sun in Sagittarius" in text
    assert "bewuste levensenergie" in text
    assert "in balans" in text


def test_build_fallback_narrative_creates_full_structure():
    points = [_point()]
    narrative = build_fallback_narrative(points)
    assert narrative["intro"]["text"]
    assert narrative["summary"]["text"]
    assert "western" in narrative["methodOverviews"]
    assert narrative["synthesis"]["text"] == "" or narrative["synthesis"]["text"] is not None


def test_generate_narrative_without_llm_returns_fallback():
    narrative = generate_narrative([_point()], llm_service=None)
    assert narrative["intro"]["generator"] == "fallback"


def test_generate_narrative_with_failing_llm_falls_back():
    class _BadLLM:
        def generate_text(self, **_kw):
            raise RuntimeError("not available")
    narrative = generate_narrative([_point()], llm_service=_BadLLM())
    method_overview = narrative["methodOverviews"]["western"]
    assert method_overview["generator"] == "fallback"
    assert "Sun in Sagittarius" in method_overview["text"]


def test_generate_narrative_with_stub_llm_uses_llm_text():
    class _StubLLM:
        def generate_text(self, **_kw):
            return "Een warme samenvatting in vloeiend Nederlands."

    narrative = generate_narrative([_point()], llm_service=_StubLLM())
    method_overview = narrative["methodOverviews"]["western"]
    assert method_overview["generator"] == "llm"
    assert "warme samenvatting" in method_overview["text"]
