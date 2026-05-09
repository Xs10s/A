# Calculation Coverage

Dit overzicht is de controlelaag tussen `calculationManifest` en `calculableValues`.

## WESTERN

| Waarde | Calculation ID | Status | Input | Output key | Result field | Energieprofiel |
|---|---|---|---|---|---|---|
| Tijdzone geboorteplaats | `western.calculate.base-astronomical-data` | implemented | birthDate,birthTime,birthPlace,timezone,coordinates | `western.base.timezone` | `western.base.context` | nee |
| Ascendant teken | `western.calculate.angles` | implemented | birthDate,birthTime,birthPlace,timezone,coordinates | `western.angles.ascendant.signId` | `western.personal.ascendant` | ja |
| Descendant teken | `western.calculate.angles` | derived | birthDate,birthTime,birthPlace,timezone,coordinates | `western.angles.descendant.signId` | `western.personal.angles` | nee |
| Zon teken | `western.calculate.planetary-positions` | implemented | calculatedWesternChart | `western.planets.sun.signId` | `western.personal.planetary-positions` | ja |
| Elementbalans vuur | `western.calculate.element-balance` | planned | calculatedWesternChart | `western.balance.elements.fire` | `western.personal.element-balance` | nee |
| Yod | `western.calculate.configurations` | planned | calculatedWesternChart | `western.configurations.yods` | `western.personal.configurations` | nee |

## VEDIC

| Waarde | Calculation ID | Status | Input | Output key | Result field | Energieprofiel |
|---|---|---|---|---|---|---|
| Ayanamsa | `vedic.calculate.base-astronomical-data` | implemented | birthDate,birthTime,timezone | `vedic.base.ayanamsha` | `vedic.base.context` | nee |
| Tithi | `vedic.calculate.panchanga` | implemented | calculatedVedicChart | `vedic.panchanga.tithi.index` | `vedic.personal.panchanga` | ja |
| Surya rashi | `vedic.calculate.sidereal-positions` | planned | calculatedVedicChart | `vedic.grahas.surya.rashi` | `vedic.personal.graha-positions` | nee |
| Lagna rashi | `vedic.calculate.lagna` | planned | calculatedVedicChart,birthPlace | `vedic.lagna.rashi` | `vedic.personal.lagna` | nee |
| Vimshottari Mahadasha | `vedic.calculate.vimshottari-dasha` | planned | calculatedVedicChart | `vedic.dashas.vimshottari.mahadasha` | `vedic.personal.dashas` | nee |

## BAZI

| Waarde | Calculation ID | Status | Input | Output key | Result field | Energieprofiel |
|---|---|---|---|---|---|---|
| Solar term | `bazi.calculate.base-calendar-data` | implemented | birthDate,birthTime,timezone | `bazi.base.solarTerm` | `bazi.base.context` | nee |
| Jaarstam | `bazi.calculate.four-pillars` | implemented | calculatedBaziChart | `bazi.pillars.year.stem` | `bazi.personal.four-pillars` | nee |
| Day Master element | `bazi.calculate.day-master` | planned | calculatedBaziChart | `bazi.dayMaster.element` | `bazi.personal.day-master` | nee |
| Direct Wealth | `bazi.calculate.ten-gods` | planned | calculatedBaziChart | `bazi.tenGods.directWealth` | `bazi.personal.ten-gods` | nee |
| Huidige Luck Pillar | `bazi.calculate.luck-pillars` | planned | calculatedBaziChart | `bazi.luckPillars.current` | `bazi.personal.luck-pillars` | ja |

## HUMAN DESIGN

| Waarde | Calculation ID | Status | Input | Output key | Result field | Energieprofiel |
|---|---|---|---|---|---|---|
| Design date/time | `human-design.calculate.base-data` | implemented | birthDate,birthTime,timezone,coordinates | `humanDesign.base.designDateTime` | `human-design.base.context` | nee |
| Personality Sun gate | `human-design.calculate.personality-activations` | implemented | calculatedHumanDesignChart | `humanDesign.personality.sun.gate` | `human-design.personal.personality-activations` | nee |
| Gedefinieerde kanalen | `human-design.calculate.channels` | implemented | calculatedHumanDesignChart | `humanDesign.channels.defined` | `human-design.personal.channels` | ja |
| Type | `human-design.calculate.type` | implemented | calculatedHumanDesignChart | `humanDesign.type` | `human-design.personal.type` | ja |
| Variables/PHS | `human-design.calculate.variables-phs` | planned | calculatedHumanDesignChart | `humanDesign.variables` | `human-design.personal.variables-phs` | nee |

## MAYA

| Waarde | Calculation ID | Status | Input | Output key | Result field | Energieprofiel |
|---|---|---|---|---|---|---|
| Kin-nummer | `maya.calculate.kin` | implemented | birthDate | `maya.kin.number` | `maya.personal.kin` | ja |
| Zonnezegel naam | `maya.calculate.seal` | implemented | birthDate | `maya.seal.name` | `maya.personal.seal` | ja |
| Galactische toonnummer | `maya.calculate.tone` | implemented | birthDate | `maya.tone.number` | `maya.personal.tone` | ja |
| Galactische signatuur | `maya.calculate.galactic-signature` | implemented | birthDate | `maya.galacticSignature.name` | `maya.personal.galactic-signature` | ja |
| Guide zegel | `maya.calculate.oracle` | planned | birthDate | `maya.oracle.guide` | `maya.personal.oracle` | nee |

## ENERGY PROFILE

| Waarde | Calculation ID | Status | Input | Output key | Result field | Energieprofiel |
|---|---|---|---|---|---|---|
| Geldige methode-resultaten | `energy-profile.calculate.method-status` | implemented | calculatedWesternChart,calculatedVedicChart,calculatedBaziChart,calculatedHumanDesignChart,calculatedMayaChart | `energyProfile.methodStatus.validMethods` | `energy-profile.method-status` | n.v.t. |
| Beweging-score | `energy-profile.calculate.theme-signals` | implemented | calculatedWesternChart,calculatedVedicChart,calculatedBaziChart | `energyProfile.themeSignals.movement` | `energy-profile.themes` | n.v.t. |
| Overlap Western + Vedic | `energy-profile.calculate.method-overlaps` | implemented | calculatedWesternChart,calculatedVedicChart | `energyProfile.overlaps.westernVedic` | `energy-profile.overlaps` | n.v.t. |
| Gecombineerde elementindicatie | `energy-profile.calculate.elementary-patterns` | planned | calculatedWesternChart,calculatedVedicChart,calculatedBaziChart,calculatedHumanDesignChart,calculatedMayaChart | `energyProfile.elementaryPatterns.combined` | `energy-profile.elementary-patterns` | n.v.t. |
| Samenvatting beschikbaar | `energy-profile.generate.summary` | implemented | calculatedWesternChart,calculatedVedicChart,calculatedBaziChart,calculatedHumanDesignChart,calculatedMayaChart | `energyProfile.summary.available` | `energy-profile.summary` | n.v.t. |

