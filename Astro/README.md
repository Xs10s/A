# Astrologische reken- en kennisbank

Reproduceerbaar, wetenschappelijk bruikbaar astrologisch rekenmotor volgens de **Specificatie voor een astrologische reken- en kennisbank** (tijdschalen, referentiekaders, methodes, JSON-output).

## Kenmerken

- **Deterministisch**: alle formules expliciet; geen stille vereenvoudigingen.
- **Laagscheiding**: A (astronomie), B (astrologie-formules), C (database), D (output).
- **Unit-safe**: alle hoeken genormaliseerd; eenheden (deg, rad, s, au) vastgelegd.
- **Traceerbaar**: elke waarde heeft context (frame, methode, confidence).

## Structuur

```
src/horoscoop/
  time_scales.py   # JD, Delta-T, TT/UT1, ERA, GMST, LST
  astronomy.py     # Coördinaten, efemeriden (SE), sunrise/sunset
  houses.py        # Placidus, Koch, Regiomontanus, Campanus, Equal, Whole Sign, Porphyry, Sripati
  sidereal.py      # Ayanāmśa, tropisch ↔ sidereaal
  aspects.py       # Hoekafstand, orb, aspect-detectie
  vedic.py         # Tithi, nakṣatra, yoga, karaṇa, vaara
  chinese.py       # Solar terms, Ganzhi, BaZi-pilaren
  engine.py        # Orkestratie → horoscoop.json
  schema.sql       # Database: kb_*, calc_run_log
  models.py        # TypedValue, BlockStatus, input/output-modellen
  json_schema.json # JSON Schema output-contract
  tests/
```

## Vereisten

- Python 3.10+
- Optioneel: **pyswisseph** (Swiss Ephemeris) voor efemeriden, huizen, sunrise; zonder SE vallen planeetposities en huizen terug op fout/placeholder.

## Installatie

```bash
pip install -r requirements.txt
```

### Swiss Ephemeris (aanbevolen)

Voor nauwkeurige posities, huizen en sunrise: installeer **pyswisseph** en plaats SE-ephemeridebestanden (bijv. `swe_ephe/`) zoals beschreven in [pyswisseph](https://pypi.org/project/pyswisseph/). Zonder SE zijn planeetposities en huizen niet beschikbaar; tijd- en kalenderblokken blijven wel berekend.

### EOP-bestand (UT1−UTC)

Voor reproduceerbare UT1 (o.a. GMST) kun je een EOP-bestand opgeven zodat UT1−UTC niet stil wordt verondersteld:

```python
from horoscoop import eop
eop.set_eop_file("/pad/naar/eop_c04.txt")  # IERS C04-achtig: mjd, x, y, ut1_utc, ...
```

Zonder EOP wordt UT1=UTC aangenomen en wordt `EOP_MISSING` in de diagnostics gezet.

## Gebruik

### CLI-voorbeeld

```bash
python -m horoscoop.cli 2000-01-01 12:00 52.0 5.0
```

### Programmatisch

```python
from horoscoop.engine import compute
out = compute(
    birth_date="2000-01-01",
    birth_time_local="12:00:00",
    lat=52.0,
    lon=5.0,
    timezone_iana="Europe/Amsterdam",
    house_system="P",
    ayanamsha_mode="Lahiri",
)
# out = dict voor horoscoop.json
```

### Chinese jaar- en daggrens

- **Jaargrens**: `chinese_year_boundary="lichun"` (Lìchūn, λ⊙=315°) of `"cny_lunisolar"` (tweede Nieuwe Maan na winterzonnewende; vereenvoudigde schrikkelmaandregel, diagnostic `CNY_LEAP_RULES_SIMPLIFIED`).
- **Daggrens**: `chinese_day_boundary="local_midnight"` of `"utc+8_midnight"` (standaard voor BaZi).
- Optioneel: `chinese_timezone_for_calendar` (standaard Asia/Shanghai bij utc+8), `chinese_include_solar_terms=True` voor 24 jieqi in het jaar.

### Vedische Pañcāṅga-modus

- **Evaluatiemoment**: `vedic_at="instant"` (geboortetijd) of `vedic_at="sunrise"` (pañcāṅga op zonsopkomst van de dag; vereist plaats).
- **Zonsopkomst**: `vedic_sunrise_method="astronomical_upper_limb"` of `"hindu_rising"` (indien ondersteund).
- Zonder plaats is sunrise-modus niet beschikbaar; in de output staat dan o.a. `VEDIC_SUNRISE_REQUIRES_LOCATION`.

### Western aspecten en orbs

- **Orb-bron**: `western_db_path="/pad/naar/kb.sqlite"` voor orbs uit de kennisbank (`kb_item` + `kb_item_property` met `orb_deg`); anders standaard in-code orbs.
- **Profiel**: `western_orb_profile="default"` (of een profielcode als de DB profielen ondersteunt).
- **Uitgebreide aspecten**: `western_extended_aspects=True` voegt o.a. quincunx, semi-square en sesquiquadrate toe. Aspecten bevatten `applying` (op basis van relatieve lengtesnelheid) en `orb_degrees`/`exact_angle_deg`.

## Database

PostgreSQL (of compatibel): migraties uitvoeren met `schema.sql`. Tabellen: `kb_item_type`, `kb_item`, `kb_property_def`, `kb_item_property`, `kb_tag`, `kb_item_tag`, `kb_interp_snippet`, `kb_interp_trigger`, `kb_weight_rule`, `kb_feature_def`, `kb_feature_rule`, `kb_source`, `kb_formula_def`, `calc_run_log`, etc.

## Tests

```bash
cd src && python -m pytest horoscoop/tests -v
```

## Bronnen

- IERS Conventions TN36 (ERA, GMST, tijdschalen)
- Swiss Ephemeris API (huizen, efemeriden, ayanāmśa, sunrise)
- Specificatie PDF: tijdschalen, database, formules, JSON-contract
- VedicDateTime (Pañcāṅga)
- YT Liu (Chinese solar terms, Ganzhi)

## Licentie

Code: zie project. Swiss Ephemeris: dual license (zie SE-documentatie).
