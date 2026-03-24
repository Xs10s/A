# Static assets (self-hosted UI)

Files in this folder are served by FastAPI at `/static/`.

| File | Purpose |
|------|---------|
| `Logowitbg.jpg` | Page background pattern (aligned with leerjouwlichaamkennen.nl kit) |
| `favicon.gif` | Browser tab icon |
| `horoscoop-westers.svg` | Banner image on the **Westers** results tab |
| `horoscoop-vedisch.svg` | Banner image on the **Sidereaals & Vedisch** results tab |
| `horoscoop-chinees.svg` | Banner image on the **Chinees & BaZi** results tab |

If you deploy without these binaries, re-download from the live site or copy from your WordPress media library, then place them here with the same filenames.

Example (PowerShell, from repo root):

```powershell
curl.exe -sL "https://leerjouwlichaamkennen.nl/wp-content/uploads/2023/09/Logowitbg.jpg" -o "app/static/Logowitbg.jpg"
```
