/**
 * Centrale metadata en UI-hulpen voor uniforme methodepagina's.
 * Zie productrichtlijn: zelfde leesroute (header, kernwaarden, chart, ...),
 * eigen inhoud per methode. Gebruikt door app/templates/index.html.
 */
(function (global) {
  "use strict";

  /** @typedef {"western"|"vedic"|"bazi"|"human_design"|"maya"} AstrologyMethodId */

  var SECTION_ORDER = [
    "header",
    "core-values",
    "chart",
    "energy-distribution",
    "life-areas",
    "dynamic-relations",
    "patterns",
    "reflection-questions",
    "technical-details",
    "glossary",
  ];

  var REGISTRY = {
    western: {
      id: "western",
      order: 1,
      methodNumber: { nl: "Methode 1", en: "Method 1" },
      title: { nl: "Westerse horoscoop", en: "Western horoscope" },
      perspective: {
        nl: "Gericht op persoonlijkheid, psychologische ontwikkeling, innerlijke dynamiek, levensgebieden en bewustwording.",
        en: "Focused on personality, psychological growth, inner dynamics, life areas, and awareness.",
      },
      sectionOrder: SECTION_ORDER,
    },
    vedic: {
      id: "vedic",
      order: 2,
      methodNumber: { nl: "Methode 2", en: "Method 2" },
      title: { nl: "Vedische horoscoop (Jyotish)", en: "Vedic horoscope (Jyotish)" },
      perspective: {
        nl: "Gericht op dharma, karma, levensrichting, timing, graha's, nakshatra's en divisiekaarten.",
        en: "Focused on dharma, karma, life direction, timing, grahas, nakshatras, and divisional charts.",
      },
      sectionOrder: SECTION_ORDER,
    },
    bazi: {
      id: "bazi",
      order: 3,
      methodNumber: { nl: "Methode 3", en: "Method 3" },
      title: { nl: "BaZi / Chinese astrologie", en: "BaZi / Chinese astrology" },
      perspective: {
        nl: "Gericht op de balans van de vijf elementen, yin/yang, de vier pilaren, levensdynamiek en structurele energie.",
        en: "Focused on five-element balance, yin/yang, the four pillars, life dynamics, and structural energy.",
      },
      sectionOrder: SECTION_ORDER,
    },
    human_design: {
      id: "human_design",
      order: 4,
      methodNumber: { nl: "Methode 4", en: "Method 4" },
      title: { nl: "Human Design", en: "Human Design" },
      perspective: {
        nl: "Gericht op energetisch functioneren, type, strategie, autoriteit, centra, poorten en kanalen.",
        en: "Focused on energetic functioning, type, strategy, authority, centers, gates, and channels.",
      },
      sectionOrder: SECTION_ORDER,
    },
    maya: {
      id: "maya",
      order: 5,
      methodNumber: { nl: "Methode 5", en: "Method 5" },
      title: { nl: "Maya tijdcyclus", en: "Maya time-cycle" },
      perspective: {
        nl: "Gericht op tijdkwaliteit, zonnezegel, toon, kin, levenspad, cyclische beweging en bewustzijnsritme.",
        en: "Focused on time quality, solar seal, tone, kin, life path, cyclic movement, and awareness rhythm.",
      },
      sectionOrder: SECTION_ORDER,
    },
  };

  /**
   * Promoveert het titelblok (h3.layout-section of h4.kundali-tech) naar <summary>
   * van een nested <details>, zodat er geen dubbele kop is.
   */
  function wrapLayoutSectionInDetails(sectionEl, defaultOpen) {
    var d = document.createElement("details");
    d.className = "method-tech-sub";
    if (defaultOpen) d.open = true;
    var s = document.createElement("summary");
    s.className = "method-tech-sub__summary";
    var h3 = sectionEl.querySelector("h3.layout-section__title");
    var h4Alt = sectionEl.querySelector("h4.kundali-tech__title");
    if (h3) {
      s.textContent = h3.textContent || "";
      h3.remove();
    } else if (h4Alt) {
      s.textContent = h4Alt.textContent || "";
      h4Alt.remove();
    } else {
      s.textContent = "Details";
    }
    d.appendChild(s);
    d.appendChild(sectionEl);
    return d;
  }

  /**
   * Buitenste inklapbare glossary: appendFn(inner) zoals appendWesternGlossaryLegend(inner).
   */
  function appendGlossaryCollapsible(parent, isNL, appendFn) {
    var d = document.createElement("details");
    d.className = "method-glossary-outer layout-section";
    d.open = false;
    var sum = document.createElement("summary");
    sum.className = "method-glossary-outer__summary";
    sum.textContent = isNL ? "Glossary" : "Glossary";
    var inner = document.createElement("div");
    inner.className = "method-glossary-outer__inner";
    appendFn(inner);
    d.appendChild(sum);
    d.appendChild(inner);
    parent.appendChild(d);
  }

  /**
   * Sectie "Vragen om mee te nemen" (zelfde grid-stijl als Westers).
   */
  function appendReflectionQuestionsSection(parent, isNL, options) {
    var opts = options || {};
    var title = opts.title != null ? opts.title : isNL ? "Vragen om mee te nemen" : "Questions to sit with";
    var lead =
      opts.lead != null
        ? opts.lead
        : isNL
          ? "Geen vaste antwoorden: open vragen om deze methode als spiegel te gebruiken, in je eigen tempo."
          : "No fixed answers: open prompts to use this method as a mirror, at your own pace.";
    var questions = Array.isArray(opts.questions) ? opts.questions.filter(Boolean) : [];
    var fallbacks = Array.isArray(opts.fallbacks) ? opts.fallbacks.filter(Boolean) : [];
    var pick = questions.length ? questions.slice(0, 8) : fallbacks.slice(0, 5);
    var section = document.createElement("article");
    section.className = "layout-section";
    var h = document.createElement("h3");
    h.className = "layout-section__title";
    h.textContent = title;
    section.appendChild(h);
    var p = document.createElement("p");
    p.className = "layout-section__lead";
    p.textContent = lead;
    section.appendChild(p);
    var grid = document.createElement("div");
    grid.className = "western-questions-grid";
    pick.forEach(function (q) {
      var item = document.createElement("blockquote");
      item.className = "western-reflect-item";
      var tx = document.createElement("p");
      tx.className = "western-reflect-item__text";
      tx.textContent = q;
      item.appendChild(tx);
      grid.appendChild(item);
    });
    section.appendChild(grid);
    parent.appendChild(section);
  }

  function baziReflectionQuestions(isNL, pillars) {
    pillars = pillars || {};
    var day = pillars.day || {};
    var ys = String(day.stem || "").trim();
    var yb = String(day.branch || "").trim();
    var dm = (ys + yb).trim();
    var qs = [];
    if (dm)
      qs.push(
        isNL
          ? "Welke elementen geven jouw Day Master (" + dm + ") kracht, en welke elementen brengen je uit balans?"
          : "Which elements strengthen your Day Master (" + dm + "), and which pull you off balance?"
      );
    qs.push(
      isNL
        ? "Waar merk je dat je natuurlijke ritme botst met wat je omgeving van je vraagt?"
        : "Where does your natural rhythm clash with what your environment expects?"
    );
    qs.push(
      isNL
        ? "Wat helpt jou om meer evenwicht te brengen tussen actie, rust, structuur en flexibiliteit?"
        : "What helps you balance action, rest, structure, and flexibility?"
    );
    return qs;
  }

  function humanDesignReflectionQuestions(isNL, hd) {
    hd = hd || {};
    var qs = [];
    if (hd.type)
      qs.push(
        isNL
          ? "Hoe voelt het wanneer je strategie en autoriteit serieus neemt bij type " + hd.type + "?"
          : "What shifts when you take strategy and authority seriously as a " + hd.type + "?"
      );
    qs.push(
      isNL
        ? "Waar probeer je energie te forceren die in jouw chart niet constant beschikbaar is?"
        : "Where might you be forcing energy that your chart does not sustain as constant?"
    );
    qs.push(
      isNL
        ? "Welke open centra maken je gevoelig voor invloed van anderen - en hoe merk je dat in het dagelijks leven?"
        : "Which open centers make you sensitive to others - and where do you notice that day to day?"
    );
    return qs;
  }

  function mayaReflectionQuestions(isNL, maya) {
    maya = maya || {};
    var tone = maya.tone || {};
    var sign = maya.sign || {};
    var qs = [];
    if (tone.name_nl || tone.name_en)
      qs.push(
        isNL
          ? "Waar nodigt jouw toon (" + (tone.name_nl || tone.name_en || "") + ") je uit tot groei, beweging of vertraging?"
          : "Where does your tone (" + (tone.name_en || tone.name_nl || "") + ") invite growth, motion, or slowing down?"
      );
    if (sign.nl || sign.en)
      qs.push(
        isNL
          ? "Hoe kun je jouw zonnezegel (" + (sign.nl || sign.en || "") + ") zien als vraag in plaats van vaststaand antwoord?"
          : "How can you read your day-sign (" + (sign.en || sign.nl || "") + ") as a question rather than a fixed answer?"
      );
    qs.push(
      isNL
        ? "Welke tijdkwaliteit herken je als terugkerend thema in je leven?"
        : "Which time-quality feels like a recurring theme in your life?"
    );
    return qs;
  }

  global.AstroMethodPage = {
    SECTION_ORDER: SECTION_ORDER,
    REGISTRY: REGISTRY,
    wrapLayoutSectionInDetails: wrapLayoutSectionInDetails,
    appendGlossaryCollapsible: appendGlossaryCollapsible,
    appendReflectionQuestionsSection: appendReflectionQuestionsSection,
    baziReflectionQuestions: baziReflectionQuestions,
    humanDesignReflectionQuestions: humanDesignReflectionQuestions,
    mayaReflectionQuestions: mayaReflectionQuestions,
  };
})(typeof window !== "undefined" ? window : globalThis);
