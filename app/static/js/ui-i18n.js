/**
 * UI strings for the horoscope form and chrome (nl, en-GB, fr-FR, de-DE).
 * Interpretive API content uses nl/en on the server; fr/de receive English text.
 */
(function (global) {
  const STRINGS = {
    "site.kicker": {
      nl: "Leer jouw lichaam kennen",
      en: "Know your body",
      fr: "Apprenez à connaître votre corps",
      de: "Lerne deinen Körper kennen",
    },
    "site.lead": {
      nl: "Dezelfde geboortedatum en -tijd, gelezen via meerdere tradities – voor meer zelfinzicht en context.",
      en: "The same birth date and time, read through several traditions – for more self-insight and context.",
      fr: "La même date et heure de naissance, lues selon plusieurs traditions – pour plus de recul et de contexte.",
      de: "Dasselbe Geburtsdatum und dieselbe Zeit, gelesen durch mehrere Traditionen – für mehr Selbsterkenntnis und Kontext.",
    },
    "form.title": { nl: "Jouw gegevens", en: "Your details", fr: "Vos données", de: "Ihre Angaben" },
    "form.lead": {
      nl: "Vul datum, tijd en plaats in. De app zoekt waar nodig breedtegraad, lengtegraad en tijdzone op.",
      en: "Enter date, time and place. The app looks up latitude, longitude and time zone where needed.",
      fr: "Saisissez la date, l'heure et le lieu. L'application recherche latitude, longitude et fuseau horaire si nécessaire.",
      de: "Geben Sie Datum, Uhrzeit und Ort ein. Die App ermittelt bei Bedarf Breitengrad, Längengrad und Zeitzone.",
    },
    "form.langLabel": { nl: "Taal", en: "Language", fr: "Langue", de: "Sprache" },
    "form.birthDate": { nl: "Geboortedatum *", en: "Date of birth *", fr: "Date de naissance *", de: "Geburtsdatum *" },
    "form.birthTime": { nl: "Geboortetijd", en: "Time of birth", fr: "Heure de naissance", de: "Geburtszeit" },
    "form.timeUnknown": { nl: "Ik weet het niet", en: "I don't know", fr: "Je ne sais pas", de: "Ich weiß es nicht" },
    "form.birthPlace": { nl: "Geboorteplaats *", en: "Place of birth *", fr: "Lieu de naissance *", de: "Geburtsort *" },
    "form.cityPlaceholder": { nl: "Amsterdam", en: "London", fr: "Paris", de: "Berlin" },
    "form.timezone": { nl: "Tijdzone", en: "Time zone", fr: "Fuseau horaire", de: "Zeitzone" },
    "form.timezoneEmpty": {
      nl: "Wordt automatisch bepaald na plaatskeuze",
      en: "Determined automatically after selecting a place",
      fr: "Déterminé automatiquement après le choix du lieu",
      de: "Wird nach Ortsauswahl automatisch ermittelt",
    },
    "form.mapPlaceholder": {
      nl: "Kies eerst een geboorteplaats om de locatie te controleren.",
      en: "Choose a birth place first to verify the location.",
      fr: "Choisissez d'abord un lieu de naissance pour vérifier l'emplacement.",
      de: "Wählen Sie zuerst einen Geburtsort, um den Standort zu prüfen.",
    },
    "form.calculate": {
      nl: "Bereken horoscoop",
      en: "Calculate horoscope",
      fr: "Calculer l'horoscope",
      de: "Horoskop berechnen",
    },
    "result.title": { nl: "Resultaat", en: "Result", fr: "Résultat", de: "Ergebnis" },
    "result.recalculate": { nl: "Opnieuw berekenen", en: "Recalculate", fr: "Recalculer", de: "Neu berechnen" },
    "result.downloadPdf": {
      nl: "Download volledig rapport (PDF)",
      en: "Download full report (PDF)",
      fr: "Télécharger le rapport complet (PDF)",
      de: "Vollständigen Bericht herunterladen (PDF)",
    },
    "tabs.energie": { nl: "Energieprofiel", en: "Energy profile", fr: "Profil énergétique", de: "Energieprofil" },
    "tabs.western": { nl: "Westers", en: "Western", fr: "Occidental", de: "Westlich" },
    "tabs.vedic": { nl: "Vedisch", en: "Vedic", fr: "Védique", de: "Vedisch" },
    "tabs.bazi": { nl: "BaZi", en: "BaZi", fr: "BaZi", de: "BaZi" },
    "tabs.humandesign": { nl: "Human Design", en: "Human Design", fr: "Human Design", de: "Human Design" },
    "tabs.maya": { nl: "Maya", en: "Maya", fr: "Maya", de: "Maya" },
    "footer.text": {
      nl: "Leer jouw lichaam kennen – horoscoop tool",
      en: "Know your body – horoscope tool",
      fr: "Apprenez à connaître votre corps – outil horoscope",
      de: "Lerne deinen Körper kennen – Horoskop-Tool",
    },
    "error.cityNotFound": {
      nl: "Geboorteplaats kon niet worden herkend.",
      en: "Birth place could not be recognised.",
      fr: "Le lieu de naissance n'a pas pu être reconnu.",
      de: "Der Geburtsort konnte nicht erkannt werden.",
    },
    "error.reportFailed": {
      nl: "Rapportdata kon niet worden opgebouwd.",
      en: "Could not build report data.",
      fr: "Impossible de construire les données du rapport.",
      de: "Berichtsdaten konnten nicht erstellt werden.",
    },
    "error.timeRequired": {
      nl: "Vul een geboortetijd in (uur en minuut) of kies Ik weet het niet.",
      en: "Enter a birth time (hours and minutes) or choose I don't know.",
      fr: "Saisissez une heure de naissance (heures et minutes) ou choisissez Je ne sais pas.",
      de: "Geben Sie eine Geburtszeit (Stunden und Minuten) ein oder wählen Sie Ich weiß es nicht.",
    },
    "place.notFound": {
      nl: "Plaats niet gevonden. Controleer de spelling.",
      en: "Place not found. Check the spelling.",
      fr: "Lieu introuvable. Vérifiez l'orthographe.",
      de: "Ort nicht gefunden. Bitte Schreibweise prüfen.",
    },
    "time.unknown": { nl: "Ik weet het niet", en: "I don't know", fr: "Je ne sais pas", de: "Ich weiß es nicht" },
    "map.previewTitle": {
      nl: "Kaartpreview van geselecteerde geboorteplaats",
      en: "Map preview of selected birth place",
      fr: "Aperçu cartographique du lieu de naissance sélectionné",
      de: "Kartenvorschau des gewählten Geburtsorts",
    },
    "stat.date": { nl: "Datum", en: "Date", fr: "Date", de: "Datum" },
    "stat.time": { nl: "Tijd", en: "Time", fr: "Heure", de: "Zeit" },
    "stat.timezone": { nl: "Tijdzone", en: "Time zone", fr: "Fuseau horaire", de: "Zeitzone" },
    "stat.place": { nl: "Plaats", en: "Place", fr: "Lieu", de: "Ort" },
    "note.timeOnlyUnknown": {
      nl: "Geboortetijd onbekend: op basis van datum en plaats tonen we wat betrouwbaar is (o.a. Maya, delen van Vedisch/BaZi). Westers (huizen, Ascendant), Human Design en het BaZi-uurpilaar vereisen een exacte tijd en zijn daarom beperkt of niet beschikbaar.",
      en: "Birth time unknown: with date and place we show what is reliable (e.g. Maya, parts of Vedic/BaZi). Western (houses, Ascendant), Human Design and the BaZi hour pillar need an exact time and are limited or unavailable.",
      fr: "Heure de naissance inconnue : avec la date et le lieu, nous affichons ce qui est fiable (p. ex. Maya, parties du Védique/BaZi). L'occidental (maisons, Ascendant), Human Design et le pilier d'heure BaZi exigent une heure exacte et sont limités ou indisponibles.",
      de: "Geburtszeit unbekannt: Mit Datum und Ort zeigen wir, was verlässlich ist (z. B. Maya, Teile von Vedisch/BaZi). Westlich (Häuser, Aszendent), Human Design und die BaZi-Stundensäule brauchen eine genaue Zeit und sind eingeschränkt oder nicht verfügbar.",
    },
    "note.incompleteGeneric": {
      nl: "Waarschuwing: invoerdata is onvolledig of deels geschat ({missing}). Voor huizen en Ascendant zijn exacte tijd, locatie en tijdzone nodig. Resultaten kunnen daardoor afwijken of gedeeltelijk ontbreken.",
      en: "Warning: input data is incomplete or partly estimated ({missing}). Exact time, location and time zone are required for houses and Ascendant. Results may differ or be partly unavailable.",
      fr: "Avertissement : les données saisies sont incomplètes ou partiellement estimées ({missing}). Une heure, un lieu et un fuseau horaire exacts sont nécessaires pour les maisons et l'Ascendant. Les résultats peuvent varier ou être partiellement indisponibles.",
      de: "Warnung: Die Eingaben sind unvollständig oder teilweise geschätzt ({missing}). Für Häuser und Aszendent sind genaue Zeit, Ort und Zeitzone nötig. Ergebnisse können abweichen oder teilweise fehlen.",
    },
    "missing.exactBirthTime": {
      nl: "exacte geboortetijd",
      en: "exact birth time",
      fr: "heure de naissance exacte",
      de: "genaue Geburtszeit",
    },
    "missing.birthLocation": {
      nl: "geboortelocatie",
      en: "birth location",
      fr: "lieu de naissance",
      de: "Geburtsort",
    },
    "missing.timezone": { nl: "tijdzone", en: "time zone", fr: "fuseau horaire", de: "Zeitzone" },
    "missing.generic": {
      nl: "één of meer invoervelden",
      en: "one or more input fields",
      fr: "un ou plusieurs champs",
      de: "ein oder mehrere Felder",
    },
  };

  const LOCALE_TAGS = { "nl-NL": "nl", "en-GB": "en", "en-US": "en", "fr-FR": "fr", "de-DE": "de" };
  const HTML_LANG = { nl: "nl-NL", en: "en-GB", fr: "fr-FR", de: "de-DE" };

  function langFromLocale(locale) {
    const key = String(locale || "nl-NL");
    if (LOCALE_TAGS[key]) return LOCALE_TAGS[key];
    const low = key.toLowerCase();
    if (low.startsWith("de")) return "de";
    if (low.startsWith("fr")) return "fr";
    if (low.startsWith("en")) return "en";
    return "nl";
  }

  function t(key, lang, vars) {
    const row = STRINGS[key];
    if (!row) return key;
    const L = lang || "nl";
    let text = row[L] || row.en || row.nl || key;
    if (vars) {
      Object.keys(vars).forEach(function (k) {
        text = text.split("{" + k + "}").join(String(vars[k]));
      });
    }
    return text;
  }

  function applyAll(locale) {
    const lang = langFromLocale(locale);
    document.documentElement.lang = HTML_LANG[lang] || "nl-NL";
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      const key = el.getAttribute("data-i18n");
      if (key) el.textContent = t(key, lang);
    });
    const city = document.getElementById("city");
    if (city) city.placeholder = t("form.cityPlaceholder", lang);
    const tzDisplay = document.getElementById("timezone-display");
    if (tzDisplay && tzDisplay.classList.contains("birth-field-readonly--empty")) {
      tzDisplay.textContent = t("form.timezoneEmpty", lang);
    }
    const mapPh = document.getElementById("place-map-placeholder");
    if (mapPh) mapPh.textContent = t("form.mapPlaceholder", lang);
    const timeUnknownLabel = document.getElementById("birth_time_unknown_label");
    if (timeUnknownLabel) timeUnknownLabel.textContent = t("form.timeUnknown", lang);
    return lang;
  }

  global.AstroUiI18n = {
    langFromLocale: langFromLocale,
    t: t,
    applyAll: applyAll,
    contentLang: function (locale) {
      return langFromLocale(locale) === "nl" ? "nl" : "en";
    },
  };
})(typeof window !== "undefined" ? window : globalThis);
