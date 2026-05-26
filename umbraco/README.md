# LJLK Horoscoop – Umbraco-integratie

Umbraco-packages voor dezelfde **compute first, save on demand**-flow als de WordPress-plugin: anoniem berekenen via de Python Horoscoop-API, opslaan na inloggen/registratie (Umbraco Members).

## Packages

| Package | Umbraco | .NET | Pad |
|---------|---------|------|-----|
| **Ljlk.Horoscoop.Umbraco8** | 8.x (getest met 8.18+) | .NET Framework 4.7.2 | `src/Ljlk.Horoscoop.Umbraco8` |
| **Ljlk.Horoscoop.Umbraco** | 10, 11, 12, 13, 14+ | .NET 8 (pas `Umbraco.Cms`-versie aan voor oudere majors) | `src/Ljlk.Horoscoop.Umbraco` |
| **Ljlk.Horoscoop.Core** | — | netstandard2.0 | gedeelde API-client, validatie, hashing |

## Vereisten

- Umbraco-site met **Members** ingeschakeld
- Externe Python Horoscoop-API (`POST /api/horoscoop`, optioneel `/api/render/wheel.svg` en `/api/render/report.pdf`)
- SQL Server (of ondersteunde Umbraco-database) voor profiel/run-tabellen

## Installatie (Umbraco 10–14)

1. Voeg een projectreferentie toe op `Ljlk.Horoscoop.Umbraco` (of installeer het NuGet-package wanneer gepubliceerd).
2. Zorg dat de assembly wordt geladen (project reference volstaat; composers worden automatisch gevonden).
3. Kopieer statische bestanden naar de site **of** laat ze uit de build-output bedienen onder `/ljlk-horoscoop/` (zie `StaticFilesComposer`).
4. Configureer in `appsettings.json`:

```json
{
  "LjlkHoroscoop": {
    "ApiBaseUrl": "https://horoscoop-api.example.com",
    "CacheSvgPdf": false,
    "MaxSavesPerUser": 10,
    "RateLimitPerHour": 60
  }
}
```

5. Start de site; migraties maken tabellen `ljlkHoroscopeProfiles` en `ljlkHoroscopeRuns`.

### Widget op een pagina (Razor)

```cshtml
@await Component.InvokeAsync("LjlkHoroscoopApp")
```

Dashboard:

```cshtml
@await Component.InvokeAsync("LjlkHoroscoopDashboard")
```

## Installatie (Umbraco 8)

1. Projectreferentie op `Ljlk.Horoscoop.Umbraco8`.
2. `Web.config` / `appSettings`:

```xml
<add key="LjlkHoroscoop:ApiBaseUrl" value="https://horoscoop-api.example.com" />
<add key="LjlkHoroscoop:CacheSvgPdf" value="false" />
<add key="LjlkHoroscoop:MaxSavesPerUser" value="10" />
<add key="LjlkHoroscoop:RateLimitPerHour" value="60" />
```

3. Kopieer `wwwroot/ljlk-horoscoop` uit de build naar de site-root (map `/ljlk-horoscoop/`).
4. In een Razor-template:

```cshtml
@using Ljlk.Horoscoop.Umbraco8.Helpers
@HoroscoopWidgetHelper.RenderApp()
```

Dashboard:

```cshtml
@HoroscoopWidgetHelper.RenderDashboard()
```

## REST API (namespace `api/ljlk/v1`)

Zelfde contract als de WordPress-plugin (`wp-json/ljlk/v1`):

| Endpoint | Methode | Auth | Beschrijving |
|----------|---------|------|--------------|
| `/compute` | POST | — | Berekening (rate limit per IP) |
| `/save` | POST | Member | Horoscoop opslaan |
| `/my` | GET | Member | Lijst opgeslagen horoscopen |
| `/register` | POST | — | Member registreren + inloggen |
| `/login` | POST | — | Member inloggen |
| `/download/json` | GET | Member | JSON-download (`run_id`) |
| `/download/wheel.svg` | GET | Member | SVG (`run_id`) |
| `/download/report.pdf` | GET | Member | PDF (`run_id`) |

Umbraco 8: routes via `UmbracoApiController` (bijv. `/umbraco/api/...` of `RoutePrefix` zoals geconfigureerd).  
Umbraco 10+: `/api/ljlk/v1/...`.

## Versiecompatibiliteit Umbraco.Cms

In `Ljlk.Horoscoop.Umbraco.csproj` staat standaard **Umbraco 13.5** op **.NET 8**. Voor andere majors:

| Umbraco | Target framework | Umbraco.Cms (voorbeeld) |
|---------|------------------|-------------------------|
| 10 | net6.0 | 10.8.x |
| 11 | net7.0 | 11.5.x |
| 12 | net8.0 | 12.3.x |
| 13–14 | net8.0 / net9.0 | 13.5+ / 14.x |

Pas `TargetFramework` en `PackageReference` aan en bouw opnieuw.

## Bouwen

```bash
cd umbraco
dotnet build Ljlk.Horoscoop.sln
```

> **Let op:** `Ljlk.Horoscoop.Umbraco8` vereist de Umbraco 8 NuGet-restore (.NET Framework). Bouw in Visual Studio of met MSBuild als `dotnet build` voor net472 beperkt is.

## Python API

Zie [README_UI.md](../README_UI.md) en de WordPress-plugin [README](../wp-content/plugins/ljlk-horoscoop/README.md) voor API-details en payload-velden.
