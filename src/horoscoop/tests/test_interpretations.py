from __future__ import annotations

from horoscoop.interpretations import (
    build_interpretations,
    interpret_western_formula,
)


def _western_block() -> dict:
    return {
        "placements": {
            "Sun": {"sign": "Aries", "degree_in_sign": 10.5, "house": 1, "retrograde": False},
            "Moon": {"sign": "Cancer", "degree_in_sign": 4.2, "house": 4, "retrograde": False},
            "Venus": {"sign": "Taurus", "degree_in_sign": 2.0, "house": 2, "retrograde": False},
            "Mars": {"sign": "Taurus", "degree_in_sign": 4.0, "house": 2, "retrograde": False},
        },
        "aspects": [
            {
                "a": "Venus",
                "b": "Mars",
                "type": "conjunction",
                "exact_angle_deg": 0.0,
                "orb_deg": 2.0,
                "applying": True,
            }
        ],
    }


def test_formula_sun_sign():
    out = interpret_western_formula("SUN | SIGN", _western_block())
    assert out["formula"] == "SUN | SIGN"
    assert out["summary"].startswith("Sun staat in Aries")
    assert out["sourceData"]["planet"] == "Sun"


def test_formula_moon_house():
    out = interpret_western_formula("MOON | HOUSE", _western_block())
    assert out["summary"] == "Moon werkt primair via huis 4."
    assert out["sourceData"]["house"] == 4


def test_formula_planet_full():
    out = interpret_western_formula("SUN | FULL", _western_block())
    assert out["summary"] == "Sun staat in Aries, huis 1."
    assert out["confidence"] == "hoog"


def test_formula_aspect_orb_check():
    out = interpret_western_formula("VENUS | CON | MARS", _western_block())
    assert out["confidence"] == "hoog"
    assert out["sourceData"]["aspect"]["orb"] == 2.0

    no_aspect = interpret_western_formula("SUN | CON | MOON", _western_block())
    assert no_aspect["summary"] == "Deze relatie is niet actief binnen de ingestelde orb."


def test_formula_invalid_body():
    out = interpret_western_formula("CHIRON | SIGN", _western_block())
    assert out["summary"].startswith("Ongeldig hemellichaam")


def test_formula_invalid_aspect():
    out = interpret_western_formula("VENUS | XYZ | MARS", _western_block())
    assert out["summary"] == "Deze formule wordt nog niet ondersteund."


def test_formula_empty_chartdata():
    out = interpret_western_formula("SUN | SIGN", {"placements": {}, "aspects": []})
    assert out["summary"] == "Nog geen horoscoopdata beschikbaar."


def test_result_without_formula_interpretations():
    out = build_interpretations({"western": None}, locale="nl-NL")
    western = out["western_tropical"]
    fi = western["formula_interpretations"]["sections"]
    assert fi["placements"][0]["summary"] == "Nog geen horoscoopdata beschikbaar."
