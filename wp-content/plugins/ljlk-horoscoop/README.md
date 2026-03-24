# LJLK Horoscoop

WordPress-plugin voor “compute first, save on demand” horoscoop op **www.leerjouwlichaamkennen.nl** (WordPress + Elementor). Anonieme bezoekers kunnen een horoscoop berekenen; bij “Opslaan” kunnen ze met alleen e-mail en wachtwoord een account aanmaken en de horoscoop bewaren.

## Vereisten

- WordPress 5.8+
- PHP 7.4+
- Externe Python Horoscoop-API (POST `/api/horoscoop`, optioneel `/api/render/wheel.svg` en `/api/render/report.pdf`)

## Installatie

1. **Plugin kopiëren**  
   Zet de map `ljlk-horoscoop` in `wp-content/plugins/`.

2. **Activeren**  
   In WP-admin: **Plugins** → **LJLK Horoscoop** → **Activeren**.  
   Bij activering worden de tabellen `{prefix}ljlk_horoscope_profiles` en `{prefix}ljlk_horoscope_runs` aangemaakt (dbDelta).

3. **Instellingen**  
   **Instellingen** → **LJLK Horoscoop**:
   - **Python API Basis-URL**: verplicht, bijv. `https://horoscoop-api.example.com` (geen slash aan het eind).
   - **SVG/PDF cachen**: optioneel; bij opslaan ook wiel (SVG) en rapport (PDF) ophalen en in de database bewaren.
   - **Max. horoscopen per gebruiker**: standaard 10.
   - **Rate limit (berekeningen per uur per IP)**: standaard 60; 0 = geen limiet.

## Shortcodes (Elementor)

- **`[ljlk_horoscoop_app]`**  
  Volledige UI: geboortedatum (verplicht), geavanceerde velden (tijd, plaats, tijdzone), knop “Berekenen”, knop “Opslaan”. Bij niet-ingelogde gebruiker: modal met alleen e-mail + wachtwoord (registreren of inloggen), daarna automatisch opslaan.

- **`[ljlk_horoscoop_dashboard]`**  
  Lijst van opgeslagen horoscopen voor de ingelogde gebruiker met links om JSON (en optioneel SVG/PDF) te downloaden. Voor gasten: melding om in te loggen.

Gebruik in Elementor: voeg een **Shortcode**-widget toe en vul bijv. `[ljlk_horoscoop_app]` in.

## REST API (namespace `wp-json/ljlk/v1`)

| Endpoint | Methode | Auth | Beschrijving |
|----------|--------|-----|--------------|
| `/compute` | POST | — | Berekening uitvoeren (rate limit per IP). Body: `birth_date` (verplicht), optioneel `birth_time`, `latitude`, `longitude`, `timezone_iana`, `utc_offset_minutes`, `settings`. |
| `/save` | POST | Cookie | Horoscoop opslaan. Zelfde body als compute; optioneel `horoscoop` (recent resultaat) om dubbele aanroep te vermijden. |
| `/my` | GET | Cookie | Lijst profielen en runs (geen PDF-blobs). |
| `/download/json?run_id=` | GET | Cookie | JSON-download. |
| `/download/wheel.svg?run_id=` | GET | Cookie | SVG-download (als gecached). |
| `/download/report.pdf?run_id=` | GET | Cookie | PDF-download (als gecached). |
| `/register` | POST | — | Registreren: body `email`, `password` (min. 10 tekens). Throttle per IP. |
| `/login` | POST | — | Inloggen: body `email`, `password`. |

Alle muterende aanroepen vanaf de frontend gebruiken de WP REST nonce (header `X-WP-Nonce`); save/my/download vereisen ingelogde gebruiker (cookie).

## Beveiliging

- Nonce voor REST-aanroepen vanaf de frontend.
- Save/list/download: alleen voor ingelogde gebruiker; `user_id` altijd via `get_current_user_id()`, nooit uit de request.
- Rate limit op `/compute` (transient per IP).
- Registratie-throttle per IP.
- Invoer gesaneerd; geboortedatum/tijd gevalideerd.
- Wachtwoorden alleen via standaard WP-registratie (`wp_create_user`).

## Gegevens

Opgeslagen per run o.a.: `user_id`, geboortedatum (en optioneel tijd, breedte/lengte, tijdzone), `settings_json`, `horoscoop_json`, optioneel `wheel_svg` en `report_pdf`. Geen namen of andere profielvelden.

## Bestandsstructuur

```
wp-content/plugins/ljlk-horoscoop/
  ljlk-horoscoop.php      # Bootstrap, activation hook
  includes/
    class-db.php          # Tabellen (dbDelta)
    class-rest.php        # REST endpoints
    class-client.php      # HTTP-client naar Python API
    class-shortcodes.php  # Shortcodes + instellingenpagina
    class-auth.php        # Rate limit, throttle, IP
    helpers.php           # Canonical hash, sanitization
  assets/
    app.js                # Frontend compute/save/auth/dashboard
    app.css               # Basisstyling
  templates/
    widget.php            # Optioneel: shortcode-wrapper
  README.md
```

## Python API

De plugin roept aan:

- **POST** `{BASE}/api/horoscoop`  
  Body o.a.: `birth_date` (YYYY-MM-DD), `birth_time_local`, `lat`, `lon`, `timezone_iana`, `utc_offset_minutes`. Antwoord: JSON (horoscoop).

- **POST** `{BASE}/api/render/wheel.svg`  
  Body: `engine_json` (horoscoop-object) of `birth_date` + overige velden. Antwoord: SVG.

- **POST** `{BASE}/api/render/report.pdf`  
  Zelfde body als wheel. Antwoord: PDF-binary.

Als SVG/PDF niet beschikbaar is, worden alleen JSON-berekeningen opgeslagen en kunnen gebruikers alleen JSON downloaden.
