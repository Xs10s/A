from __future__ import annotations

from .types import CalculableValueDefinition


def _v(
    *,
    value_id: str,
    method: str,
    category: str,
    label: str,
    calculation_id: str | None,
    output_key: str | None,
    required_inputs: list[str],
    status: str,
    used_fields: list[str],
    in_energy: bool = False,
    fallback: str | None = None,
    derived_from: list[str] | None = None,
) -> CalculableValueDefinition:
    out: CalculableValueDefinition = {
        "id": value_id,
        "method": method,  # type: ignore[typeddict-item]
        "category": category,
        "label": label,
        "requiredInputs": required_inputs,  # type: ignore[typeddict-item]
        "status": status,  # type: ignore[typeddict-item]
        "usedInResultFields": used_fields,
        "usedInEnergyProfile": in_energy,
    }
    if calculation_id:
        out["calculationId"] = calculation_id
    if output_key:
        out["outputKey"] = output_key
    if fallback:
        out["fallbackMessage"] = fallback
    if derived_from:
        out["derivedFrom"] = derived_from
    return out


CALCULABLE_VALUES: list[CalculableValueDefinition] = []


def _add(defn: CalculableValueDefinition) -> None:
    CALCULABLE_VALUES.append(defn)


def _seed_values() -> None:
    # WESTERN
    _add(_v(value_id="western.base.timezone", method="western", category="base", label="Tijdzone geboorteplaats", calculation_id="western.calculate.base-astronomical-data", output_key="western.base.timezone", required_inputs=["birthDate", "birthTime", "birthPlace", "timezone", "coordinates"], status="implemented", used_fields=["western.base.context"]))
    _add(_v(value_id="western.base.utc-birth-time", method="western", category="base", label="UTC-geboortetijd", calculation_id="western.calculate.base-astronomical-data", output_key="western.base.utcBirthTime", required_inputs=["birthDate", "birthTime", "timezone"], status="implemented", used_fields=["western.base.context"]))
    _add(_v(value_id="western.base.julian-day", method="western", category="base", label="Julian Day", calculation_id="western.calculate.base-astronomical-data", output_key="western.base.julianDay", required_inputs=["birthDate", "birthTime", "timezone"], status="implemented", used_fields=["western.base.context"]))
    _add(_v(value_id="western.base.local-sidereal-time", method="western", category="base", label="Lokale siderische tijd", calculation_id="western.calculate.base-astronomical-data", output_key="western.base.localSiderealTime", required_inputs=["birthDate", "birthTime", "birthPlace", "timezone", "coordinates"], status="implemented", used_fields=["western.base.context"]))
    _add(_v(value_id="western.base.latitude", method="western", category="base", label="Breedtegraad", calculation_id="western.calculate.base-astronomical-data", output_key="western.base.latitude", required_inputs=["birthDate", "birthTime", "birthPlace", "coordinates"], status="implemented", used_fields=["western.base.context"]))
    _add(_v(value_id="western.base.longitude", method="western", category="base", label="Lengtegraad", calculation_id="western.calculate.base-astronomical-data", output_key="western.base.longitude", required_inputs=["birthDate", "birthTime", "birthPlace", "coordinates"], status="implemented", used_fields=["western.base.context"]))

    for planet in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "chiron"]:
        label = planet.capitalize()
        _add(_v(value_id=f"western.planets.{planet}.sign", method="western", category="planetary-positions", label=f"{label} teken", calculation_id="western.calculate.planetary-positions", output_key=f"western.planets.{planet}.signId", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.planetary-positions"], in_energy=planet in {"sun", "moon"}))
        _add(_v(value_id=f"western.planets.{planet}.degree", method="western", category="planetary-positions", label=f"{label} graad", calculation_id="western.calculate.planetary-positions", output_key=f"western.planets.{planet}.degree", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.planetary-positions"]))
        _add(_v(value_id=f"western.planets.{planet}.house", method="western", category="planetary-positions", label=f"{label} huis", calculation_id="western.calculate.planet-house-placements", output_key=f"western.placements.{planet}.house", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.planet-house-placements"]))
        if planet not in {"sun", "moon"}:
            _add(_v(value_id=f"western.planets.{planet}.retrograde", method="western", category="retrogrades", label=f"{label} retrograde-status", calculation_id="western.calculate.retrogrades", output_key=f"western.retrogrades.{planet}", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.retrogrades"]))

    for node in ["north", "south"]:
        _add(_v(value_id=f"western.nodes.{node}.sign", method="western", category="nodes", label=f"{'Noordelijke' if node == 'north' else 'Zuidelijke'} maansknoop teken", calculation_id="western.calculate.nodes", output_key=f"western.nodes.{node}.signId", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.nodes"]))
        _add(_v(value_id=f"western.nodes.{node}.degree", method="western", category="nodes", label=f"{'Noordelijke' if node == 'north' else 'Zuidelijke'} maansknoop graad", calculation_id="western.calculate.nodes", output_key=f"western.nodes.{node}.degree", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.nodes"]))
        _add(_v(value_id=f"western.nodes.{node}.house", method="western", category="nodes", label=f"{'Noordelijke' if node == 'north' else 'Zuidelijke'} maansknoop huis", calculation_id="western.calculate.nodes", output_key=f"western.nodes.{node}.house", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.nodes"]))

    _add(_v(value_id="western.ascendant.sign", method="western", category="angles", label="Ascendant teken", calculation_id="western.calculate.angles", output_key="western.angles.ascendant.signId", required_inputs=["birthDate", "birthTime", "birthPlace", "timezone", "coordinates"], status="implemented", used_fields=["western.personal.ascendant"], in_energy=True, fallback="De ascendant kan niet worden berekend zonder geboortetijd en geboorteplaats."))
    _add(_v(value_id="western.ascendant.degree", method="western", category="angles", label="Ascendant graad", calculation_id="western.calculate.angles", output_key="western.angles.ascendant.degree", required_inputs=["birthDate", "birthTime", "birthPlace", "timezone", "coordinates"], status="implemented", used_fields=["western.personal.ascendant"], in_energy=True))
    _add(_v(value_id="western.descendant.sign", method="western", category="angles", label="Descendant teken", calculation_id="western.calculate.angles", output_key="western.angles.descendant.signId", required_inputs=["birthDate", "birthTime", "birthPlace", "timezone", "coordinates"], status="derived", used_fields=["western.personal.angles"], derived_from=["western.ascendant.sign"]))
    _add(_v(value_id="western.descendant.degree", method="western", category="angles", label="Descendant graad", calculation_id="western.calculate.angles", output_key="western.angles.descendant.degree", required_inputs=["birthDate", "birthTime", "birthPlace", "timezone", "coordinates"], status="derived", used_fields=["western.personal.angles"], derived_from=["western.ascendant.degree"]))
    _add(_v(value_id="western.mc.sign", method="western", category="angles", label="MC teken", calculation_id="western.calculate.angles", output_key="western.angles.mc.signId", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.angles"]))
    _add(_v(value_id="western.mc.degree", method="western", category="angles", label="MC graad", calculation_id="western.calculate.angles", output_key="western.angles.mc.degree", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.angles"]))
    _add(_v(value_id="western.ic.sign", method="western", category="angles", label="IC teken", calculation_id="western.calculate.angles", output_key="western.angles.ic.signId", required_inputs=["calculatedWesternChart"], status="derived", used_fields=["western.personal.angles"], derived_from=["western.mc.sign"]))
    _add(_v(value_id="western.ic.degree", method="western", category="angles", label="IC graad", calculation_id="western.calculate.angles", output_key="western.angles.ic.degree", required_inputs=["calculatedWesternChart"], status="derived", used_fields=["western.personal.angles"], derived_from=["western.mc.degree"]))

    for n in range(1, 13):
        _add(_v(value_id=f"western.houses.{n}.cusp-sign", method="western", category="houses", label=f"Huis {n} cusp teken", calculation_id="western.calculate.houses", output_key=f"western.houses.cusps.{n}.signId", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.houses"]))
        _add(_v(value_id=f"western.houses.{n}.cusp-degree", method="western", category="houses", label=f"Huis {n} cusp graad", calculation_id="western.calculate.houses", output_key=f"western.houses.cusps.{n}.degree", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.houses"]))

    for aspect in ["conjunctions", "sextiles", "squares", "trines", "oppositions", "quincunxes", "semisextiles", "semisquares", "sesquiquadrates", "orbs", "applying-separating"]:
        _add(_v(value_id=f"western.aspects.{aspect}", method="western", category="aspects", label=f"Aspecten: {aspect}", calculation_id="western.calculate.aspects", output_key=f"western.aspects.{aspect}", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.aspects"]))

    for bal, calc_id in [("elements", "western.calculate.element-balance"), ("modalities", "western.calculate.modality-balance"), ("polarity", "western.calculate.polarity-balance")]:
        for key in {"elements": ["fire", "earth", "air", "water"], "modalities": ["cardinal", "fixed", "mutable"], "polarity": ["yin", "yang"]}[bal]:
            _add(_v(value_id=f"western.balance.{bal}.{key}", method="western", category="balances", label=f"{bal} {key} score", calculation_id=calc_id, output_key=f"western.balance.{bal}.{key}", required_inputs=["calculatedWesternChart"], status="planned", used_fields=[f"western.personal.{bal}-balance"], in_energy=bal == "elements"))

    for conf in ["stelliums", "t-squares", "grand-trines", "grand-crosses", "yods", "kites", "mystic-rectangles", "bowl-pattern", "splash-pattern", "bundle-pattern", "locomotive-pattern", "see-saw-pattern"]:
        _add(_v(value_id=f"western.configurations.{conf}", method="western", category="configurations", label=conf, calculation_id="western.calculate.configurations", output_key=f"western.configurations.{conf}", required_inputs=["calculatedWesternChart"], status="planned", used_fields=["western.personal.configurations"]))

    for dig in ["domicile", "exaltation", "detriment", "fall", "peregrine", "house-rulers", "dispositors", "final-dispositor"]:
        _add(_v(value_id=f"western.dignities.{dig}", method="western", category="dignities", label=dig, calculation_id="western.calculate.dignities", output_key=f"western.dignities.{dig}", required_inputs=["calculatedWesternChart"], status="planned", used_fields=["western.personal.dignities"]))

    for opt in ["pars-fortunae", "vertex", "lilith", "ceres", "pallas", "juno", "vesta", "sect", "dominant-planet", "dominant-element", "dominant-sign", "dominant-house", "chart-ruler"]:
        _add(_v(value_id=f"western.optional.{opt}", method="western", category="optional", label=opt, calculation_id="western.calculate.dominants", output_key=f"western.optional.{opt}", required_inputs=["calculatedWesternChart"], status="planned", used_fields=["western.personal.optional"]))

    # VEDIC / BAZI / HD / MAYA / ENERGY PROFILE representative + status control.
    _add(_v(value_id="vedic.base.ayanamsa", method="vedic", category="base", label="Ayanamsa", calculation_id="vedic.calculate.base-astronomical-data", output_key="vedic.base.ayanamsha", required_inputs=["birthDate", "birthTime", "timezone"], status="implemented", used_fields=["vedic.base.context"]))
    for k in ["surya", "chandra", "mangala", "budha", "guru", "shukra", "shani", "rahu", "ketu"]:
        _add(_v(value_id=f"vedic.grahas.{k}.rashi", method="vedic", category="graha-positions", label=f"{k} rashi", calculation_id="vedic.calculate.sidereal-positions", output_key=f"vedic.grahas.{k}.rashi", required_inputs=["calculatedVedicChart"], status="planned", used_fields=["vedic.personal.graha-positions"]))
    for k in ["tithi", "vaara", "nakshatra", "yoga", "karana", "paksha", "moon-phase"]:
        _add(_v(value_id=f"vedic.panchanga.{k}", method="vedic", category="panchanga", label=k, calculation_id="vedic.calculate.panchanga", output_key=f"vedic.panchanga.{k}", required_inputs=["calculatedVedicChart"], status="implemented", used_fields=["vedic.personal.panchanga"], in_energy=True))
    for group, calc in [("dashas", "vedic.calculate.vimshottari-dasha"), ("vargas", "vedic.calculate.vargas"), ("drishti", "vedic.calculate.drishti"), ("yogas", "vedic.calculate.yogas"), ("karakas", "vedic.calculate.karakas"), ("dignities-strengths", "vedic.calculate.dignities-strengths")]:
        _add(_v(value_id=f"vedic.{group}.core", method="vedic", category=group, label=group, calculation_id=calc, output_key=f"vedic.{group}.core", required_inputs=["calculatedVedicChart"], status="planned", used_fields=[f"vedic.personal.{group}"]))

    _add(_v(value_id="bazi.base.solar-term", method="bazi", category="base", label="Solar term", calculation_id="bazi.calculate.base-calendar-data", output_key="bazi.base.solarTerm", required_inputs=["birthDate", "birthTime", "timezone"], status="implemented", used_fields=["bazi.base.context"]))
    for pillar in ["year", "month", "day", "hour"]:
        for part in ["stem", "branch"]:
            _add(_v(value_id=f"bazi.pillars.{pillar}.{part}", method="bazi", category="four-pillars", label=f"{pillar} {part}", calculation_id="bazi.calculate.four-pillars", output_key=f"bazi.pillars.{pillar}.{part}", required_inputs=["calculatedBaziChart"], status="implemented", used_fields=["bazi.personal.four-pillars"]))
    for grp, calc in [("day-master", "bazi.calculate.day-master"), ("heavenly-stems", "bazi.calculate.heavenly-stems"), ("earthly-branches", "bazi.calculate.earthly-branches"), ("hidden-stems", "bazi.calculate.hidden-stems"), ("element-balance", "bazi.calculate.element-balance"), ("yin-yang-balance", "bazi.calculate.yin-yang-balance"), ("ten-gods", "bazi.calculate.ten-gods"), ("interactions", "bazi.calculate.interactions"), ("chart-structure", "bazi.calculate.chart-structure"), ("useful-elements", "bazi.calculate.useful-elements"), ("luck-pillars", "bazi.calculate.luck-pillars"), ("annual-cycle", "bazi.calculate.annual-cycle")]:
        _add(_v(value_id=f"bazi.{grp}.core", method="bazi", category=grp, label=grp, calculation_id=calc, output_key=f"bazi.{grp}.core", required_inputs=["calculatedBaziChart"], status="planned", used_fields=[f"bazi.personal.{grp}"], in_energy=grp in {"element-balance", "luck-pillars"}))

    _add(_v(value_id="human-design.base.design-datetime", method="human-design", category="base", label="Design date/time", calculation_id="human-design.calculate.base-data", output_key="humanDesign.base.designDateTime", required_inputs=["birthDate", "birthTime", "timezone", "coordinates"], status="implemented", used_fields=["human-design.base.context"]))
    for grp, calc, st in [("personality-activations", "human-design.calculate.personality-activations", "implemented"), ("design-activations", "human-design.calculate.design-activations", "implemented"), ("gates", "human-design.calculate.gates", "implemented"), ("channels", "human-design.calculate.channels", "implemented"), ("centers", "human-design.calculate.centers", "implemented"), ("type", "human-design.calculate.type", "implemented"), ("strategy", "human-design.calculate.strategy", "implemented"), ("authority", "human-design.calculate.authority", "implemented"), ("profile", "human-design.calculate.profile", "implemented"), ("definition", "human-design.calculate.definition", "planned"), ("incarnation-cross", "human-design.calculate.incarnation-cross", "implemented"), ("conditioning", "human-design.calculate.conditioning", "planned"), ("variables-phs", "human-design.calculate.variables-phs", "planned")]:
        _add(_v(value_id=f"human-design.{grp}.core", method="human-design", category=grp, label=grp, calculation_id=calc, output_key=f"humanDesign.{grp}.core", required_inputs=["calculatedHumanDesignChart"], status=st, used_fields=[f"human-design.personal.{grp}"], in_energy=grp in {"channels", "centers", "type", "strategy", "authority"}))

    for grp, calc, st in [("kin", "maya.calculate.kin", "implemented"), ("seal", "maya.calculate.seal", "implemented"), ("tone", "maya.calculate.tone", "implemented"), ("galactic-signature", "maya.calculate.galactic-signature", "implemented"), ("wavespell", "maya.calculate.wavespell", "implemented"), ("castle", "maya.calculate.castle", "planned"), ("oracle", "maya.calculate.oracle", "planned"), ("time-cycles", "maya.calculate.time-cycles", "planned"), ("dreamspell-extensions", "maya.calculate.dreamspell-extensions", "planned")]:
        _add(_v(value_id=f"maya.{grp}.core", method="maya", category=grp, label=grp, calculation_id=calc, output_key=f"maya.{grp}.core", required_inputs=["birthDate"], status=st, used_fields=[f"maya.personal.{grp}"], in_energy=grp in {"kin", "seal", "tone", "galactic-signature"}))

    for grp, calc, st in [("method-status", "energy-profile.calculate.method-status", "implemented"), ("theme-signals", "energy-profile.calculate.theme-signals", "implemented"), ("method-overlaps", "energy-profile.calculate.method-overlaps", "implemented"), ("method-contrasts", "energy-profile.calculate.method-contrasts", "planned"), ("elementary-patterns", "energy-profile.calculate.elementary-patterns", "planned"), ("summary-patterns", "energy-profile.calculate.summary-patterns", "implemented"), ("summary", "energy-profile.generate.summary", "implemented")]:
        _add(_v(value_id=f"energy-profile.{grp}.core", method="energy-profile", category=grp, label=grp, calculation_id=calc, output_key=f"energyProfile.{grp}.core", required_inputs=["calculatedWesternChart", "calculatedVedicChart", "calculatedBaziChart", "calculatedHumanDesignChart", "calculatedMayaChart"], status=st, used_fields=[f"energy-profile.{grp}"]))


_seed_values()


_LEGACY_VALUES: list[CalculableValueDefinition] = [
    _v(value_id="western.base.timezone", method="western", category="base", label="Tijdzone geboorteplaats", calculation_id="western.calculate.base-astronomical-data", output_key="western.base.timezone", required_inputs=["birthDate", "birthTime", "birthPlace", "timezone", "coordinates"], status="implemented", used_fields=["western.base.context"]),
    _v(value_id="western.base.utc-birth-time", method="western", category="base", label="UTC-geboortetijd", calculation_id="western.calculate.base-astronomical-data", output_key="western.base.utcBirthTime", required_inputs=["birthDate", "birthTime", "timezone"], status="implemented", used_fields=["western.base.context"]),
    _v(value_id="western.base.julian-day", method="western", category="base", label="Julian Day", calculation_id="western.calculate.base-astronomical-data", output_key="western.base.julianDay", required_inputs=["birthDate", "birthTime", "timezone"], status="implemented", used_fields=["western.base.context"]),
    _v(value_id="western.ascendant.sign", method="western", category="angles", label="Ascendant teken", calculation_id="western.calculate.angles", output_key="western.angles.ascendant.signId", required_inputs=["birthDate", "birthTime", "birthPlace", "timezone", "coordinates"], status="implemented", used_fields=["western.personal.ascendant"], in_energy=True, fallback="De ascendant kan niet worden berekend zonder geboortetijd en geboorteplaats."),
    _v(value_id="western.ascendant.degree", method="western", category="angles", label="Ascendant graad", calculation_id="western.calculate.angles", output_key="western.angles.ascendant.degree", required_inputs=["birthDate", "birthTime", "birthPlace", "timezone", "coordinates"], status="implemented", used_fields=["western.personal.ascendant"], in_energy=True, fallback="De ascendantgraad kan niet worden berekend zonder geboortetijd en geboorteplaats."),
    _v(value_id="western.descendant.sign", method="western", category="angles", label="Descendant teken", calculation_id="western.calculate.angles", output_key="western.angles.descendant.signId", required_inputs=["birthDate", "birthTime", "birthPlace", "timezone", "coordinates"], status="derived", used_fields=["western.personal.angles"], derived_from=["western.ascendant.sign"]),
    _v(value_id="western.planets.sun.sign", method="western", category="planetary-positions", label="Zon teken", calculation_id="western.calculate.planetary-positions", output_key="western.planets.sun.signId", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.planetary-positions"], in_energy=True),
    _v(value_id="western.planets.moon.sign", method="western", category="planetary-positions", label="Maan teken", calculation_id="western.calculate.planetary-positions", output_key="western.planets.moon.signId", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.planetary-positions"], in_energy=True),
    _v(value_id="western.planets.mercury.retrograde", method="western", category="planetary-positions", label="Mercurius retrograde-status", calculation_id="western.calculate.retrogrades", output_key="western.retrogrades.mercury", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.retrogrades"]),
    _v(value_id="western.houses.cusp-1", method="western", category="houses", label="Huis 1 cusp", calculation_id="western.calculate.houses", output_key="western.houses.cusps.1", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.houses"]),
    _v(value_id="western.aspects.conjunctions", method="western", category="aspects", label="Conjuncties", calculation_id="western.calculate.aspects", output_key="western.aspects.list.conjunctions", required_inputs=["calculatedWesternChart"], status="implemented", used_fields=["western.personal.aspects"]),
    _v(value_id="western.balance.elements.fire", method="western", category="balances", label="Vuur-score", calculation_id="western.calculate.element-balance", output_key="western.balance.elements.fire", required_inputs=["calculatedWesternChart"], status="planned", used_fields=["western.personal.element-balance"]),
    _v(value_id="western.configurations.yod", method="western", category="configurations", label="Yod", calculation_id="western.calculate.configurations", output_key="western.configurations.yods", required_inputs=["calculatedWesternChart"], status="planned", used_fields=["western.personal.configurations"], fallback="Yod-detectie is inhoudelijk voorbereid, maar nog niet actief in deze versie."),
    _v(value_id="western.dignities.domicile", method="western", category="dignities", label="Domicile", calculation_id="western.calculate.dignities", output_key="western.dignities.domicile", required_inputs=["calculatedWesternChart"], status="planned", used_fields=["western.personal.dignities"]),
    _v(value_id="western.optional.pars-fortunae", method="western", category="optional", label="Pars Fortunae", calculation_id="western.calculate.dominants", output_key="western.optional.parsFortunae", required_inputs=["calculatedWesternChart"], status="planned", used_fields=["western.personal.optional"]),
    _v(value_id="vedic.base.ayanamsa", method="vedic", category="base", label="Ayanamsa", calculation_id="vedic.calculate.base-astronomical-data", output_key="vedic.base.ayanamsha", required_inputs=["birthDate", "birthTime", "timezone"], status="implemented", used_fields=["vedic.base.context"]),
    _v(value_id="vedic.panchanga.tithi", method="vedic", category="panchanga", label="Tithi", calculation_id="vedic.calculate.panchanga", output_key="vedic.panchanga.tithi.index", required_inputs=["calculatedVedicChart"], status="implemented", used_fields=["vedic.personal.panchanga"], in_energy=True),
    _v(value_id="vedic.grahas.surya.rashi", method="vedic", category="graha-positions", label="Surya rashi", calculation_id="vedic.calculate.sidereal-positions", output_key="vedic.grahas.surya.rashi", required_inputs=["calculatedVedicChart"], status="planned", used_fields=["vedic.personal.graha-positions"]),
    _v(value_id="vedic.lagna.rashi", method="vedic", category="lagna-bhava", label="Lagna rashi", calculation_id="vedic.calculate.lagna", output_key="vedic.lagna.rashi", required_inputs=["calculatedVedicChart", "birthPlace"], status="planned", used_fields=["vedic.personal.lagna"]),
    _v(value_id="vedic.vimshottari.mahadasha", method="vedic", category="dashas", label="Vimshottari Mahadasha", calculation_id="vedic.calculate.vimshottari-dasha", output_key="vedic.dashas.vimshottari.mahadasha", required_inputs=["calculatedVedicChart"], status="planned", used_fields=["vedic.personal.dashas"]),
    _v(value_id="vedic.vargas.d9", method="vedic", category="vargas", label="D9 Navamsha", calculation_id="vedic.calculate.vargas", output_key="vedic.vargas.D9", required_inputs=["calculatedVedicChart"], status="planned", used_fields=["vedic.personal.vargas"]),
    _v(value_id="bazi.base.solar-term", method="bazi", category="base", label="Solar term", calculation_id="bazi.calculate.base-calendar-data", output_key="bazi.base.solarTerm", required_inputs=["birthDate", "birthTime", "timezone"], status="implemented", used_fields=["bazi.base.context"]),
    _v(value_id="bazi.pillars.year.stem", method="bazi", category="four-pillars", label="Jaarstam", calculation_id="bazi.calculate.four-pillars", output_key="bazi.pillars.year.stem", required_inputs=["calculatedBaziChart"], status="implemented", used_fields=["bazi.personal.four-pillars"]),
    _v(value_id="bazi.day-master.element", method="bazi", category="day-master", label="Day Master element", calculation_id="bazi.calculate.day-master", output_key="bazi.dayMaster.element", required_inputs=["calculatedBaziChart"], status="planned", used_fields=["bazi.personal.day-master"]),
    _v(value_id="bazi.ten-gods.direct-wealth", method="bazi", category="ten-gods", label="Direct Wealth", calculation_id="bazi.calculate.ten-gods", output_key="bazi.tenGods.directWealth", required_inputs=["calculatedBaziChart"], status="planned", used_fields=["bazi.personal.ten-gods"]),
    _v(value_id="bazi.luck-pillars.current", method="bazi", category="luck-pillars", label="Huidige Luck Pillar", calculation_id="bazi.calculate.luck-pillars", output_key="bazi.luckPillars.current", required_inputs=["calculatedBaziChart"], status="planned", used_fields=["bazi.personal.luck-pillars"], in_energy=True),
    _v(value_id="human-design.base.design-datetime", method="human-design", category="base", label="Design date/time", calculation_id="human-design.calculate.base-data", output_key="humanDesign.base.designDateTime", required_inputs=["birthDate", "birthTime", "timezone", "coordinates"], status="implemented", used_fields=["human-design.base.context"]),
    _v(value_id="human-design.activations.personality-sun-gate", method="human-design", category="activations", label="Personality Sun gate", calculation_id="human-design.calculate.personality-activations", output_key="humanDesign.personality.sun.gate", required_inputs=["calculatedHumanDesignChart"], status="implemented", used_fields=["human-design.personal.personality-activations"]),
    _v(value_id="human-design.channels.defined", method="human-design", category="channels", label="Gedefinieerde kanalen", calculation_id="human-design.calculate.channels", output_key="humanDesign.channels.defined", required_inputs=["calculatedHumanDesignChart"], status="implemented", used_fields=["human-design.personal.channels"], in_energy=True),
    _v(value_id="human-design.centers.sacral", method="human-design", category="centers", label="Sacral center status", calculation_id="human-design.calculate.centers", output_key="humanDesign.centers.sacral", required_inputs=["calculatedHumanDesignChart"], status="implemented", used_fields=["human-design.personal.centers"], in_energy=True),
    _v(value_id="human-design.type", method="human-design", category="type-strategy-authority", label="Type", calculation_id="human-design.calculate.type", output_key="humanDesign.type", required_inputs=["calculatedHumanDesignChart"], status="implemented", used_fields=["human-design.personal.type"], in_energy=True),
    _v(value_id="human-design.variables.phs", method="human-design", category="variables-phs", label="Variables / PHS", calculation_id="human-design.calculate.variables-phs", output_key="humanDesign.variables", required_inputs=["calculatedHumanDesignChart"], status="planned", used_fields=["human-design.personal.variables-phs"]),
    _v(value_id="maya.kin.number", method="maya", category="kin", label="Kin-nummer", calculation_id="maya.calculate.kin", output_key="maya.kin.number", required_inputs=["birthDate"], status="implemented", used_fields=["maya.personal.kin"], in_energy=True),
    _v(value_id="maya.seal.name", method="maya", category="seal", label="Zonnezegel naam", calculation_id="maya.calculate.seal", output_key="maya.seal.name", required_inputs=["birthDate"], status="implemented", used_fields=["maya.personal.seal"], in_energy=True),
    _v(value_id="maya.tone.number", method="maya", category="tone", label="Galactische toonnummer", calculation_id="maya.calculate.tone", output_key="maya.tone.number", required_inputs=["birthDate"], status="implemented", used_fields=["maya.personal.tone"], in_energy=True),
    _v(value_id="maya.signature.name", method="maya", category="galactic-signature", label="Volledige signatuurnaam", calculation_id="maya.calculate.galactic-signature", output_key="maya.galacticSignature.name", required_inputs=["birthDate"], status="implemented", used_fields=["maya.personal.galactic-signature"], in_energy=True),
    _v(value_id="maya.oracle.guide-seal", method="maya", category="oracle", label="Guide zegel", calculation_id="maya.calculate.oracle", output_key="maya.oracle.guide", required_inputs=["birthDate"], status="planned", used_fields=["maya.personal.oracle"]),
    _v(value_id="energy-profile.methods.valid", method="energy-profile", category="method-status", label="Geldige methode-resultaten", calculation_id="energy-profile.calculate.method-status", output_key="energyProfile.methodStatus.validMethods", required_inputs=["calculatedWesternChart", "calculatedVedicChart", "calculatedBaziChart", "calculatedHumanDesignChart", "calculatedMayaChart"], status="implemented", used_fields=["energy-profile.method-status"]),
    _v(value_id="energy-profile.theme.movement", method="energy-profile", category="themes", label="Beweging-score", calculation_id="energy-profile.calculate.theme-signals", output_key="energyProfile.themeSignals.movement", required_inputs=["calculatedWesternChart", "calculatedVedicChart", "calculatedBaziChart"], status="implemented", used_fields=["energy-profile.themes"]),
    _v(value_id="energy-profile.overlap.western-vedic", method="energy-profile", category="method-overlaps", label="Overlap Western + Vedic", calculation_id="energy-profile.calculate.method-overlaps", output_key="energyProfile.overlaps.westernVedic", required_inputs=["calculatedWesternChart", "calculatedVedicChart"], status="implemented", used_fields=["energy-profile.overlaps"]),
    _v(value_id="energy-profile.patterns.elementary", method="energy-profile", category="elementary-patterns", label="Gecombineerde elementindicatie", calculation_id="energy-profile.calculate.elementary-patterns", output_key="energyProfile.elementaryPatterns.combined", required_inputs=["calculatedWesternChart", "calculatedVedicChart", "calculatedBaziChart", "calculatedHumanDesignChart", "calculatedMayaChart"], status="planned", used_fields=["energy-profile.elementary-patterns"]),
    _v(value_id="energy-profile.summary.available", method="energy-profile", category="summary-status", label="Samenvatting beschikbaar", calculation_id="energy-profile.generate.summary", output_key="energyProfile.summary.available", required_inputs=["calculatedWesternChart", "calculatedVedicChart", "calculatedBaziChart", "calculatedHumanDesignChart", "calculatedMayaChart"], status="implemented", used_fields=["energy-profile.summary"]),
]


def get_calculable_values() -> list[CalculableValueDefinition]:
    # Legacy explicit subset is appended for backwards compatibility with
    # previously referenced value IDs in templates/tests.
    return list(CALCULABLE_VALUES + _LEGACY_VALUES)

