(function () {
  'use strict';

  var conf = window.ljlkHoroscoop || {};
  var restUrl = conf.restUrl || '';
  var nonce = conf.nonce || '';
  var loggedIn = conf.loggedIn === true;
  var i18n = conf.i18n || {};

  function get(name) {
    return function (el) {
      return (el || document).querySelector(name);
    };
  }
  function getAll(name, el) {
    return Array.prototype.slice.call((el || document).querySelectorAll(name));
  }

  function getPayload() {
    var birthDate = (get('#ljlk-birth-date') && get('#ljlk-birth-date').value) || '';
    var payload = { birth_date: birthDate };
    var time = get('#ljlk-birth-time') && get('#ljlk-birth-time').value;
    if (time) payload.birth_time = time;
    var lat = get('#ljlk-latitude') && get('#ljlk-latitude').value;
    if (lat !== '' && !isNaN(parseFloat(lat))) payload.latitude = parseFloat(lat);
    var lon = get('#ljlk-longitude') && get('#ljlk-longitude').value;
    if (lon !== '' && !isNaN(parseFloat(lon))) payload.longitude = parseFloat(lon);
    var tz = get('#ljlk-timezone') && get('#ljlk-timezone').value;
    if (tz) payload.timezone_iana = tz;
    var utc = get('#ljlk-utc-offset') && get('#ljlk-utc-offset').value;
    if (utc !== '' && !isNaN(parseInt(utc, 10))) payload.utc_offset_minutes = parseInt(utc, 10);
    return payload;
  }

  function fetchOptions(method, body) {
    var opt = {
      method: method || 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    };
    if (body !== undefined) opt.body = typeof body === 'string' ? body : JSON.stringify(body);
    return opt;
  }

  function showError(container, message) {
    if (!container) return;
    container.innerHTML = '<div class="ljlk-error" role="alert">' + (i18n.error || 'Fout') + ': ' + escapeHtml(message) + '</div>';
    container.hidden = false;
  }

  function escapeHtml(s) {
    if (s == null) return '';
    var div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function formatI18n(template, vars) {
    var out = String(template || '');
    Object.keys(vars || {}).forEach(function (k) {
      out = out.split('{' + k + '}').join(String(vars[k]));
    });
    return out;
  }

  function renderBlock(block, title) {
    if (block == null || (typeof block === 'object' && Object.keys(block).length === 0)) {
      return '<p class="ljlk-block-empty">—</p>';
    }
    if (typeof block !== 'object') {
      return '<p>' + escapeHtml(String(block)) + '</p>';
    }
    var rows = [];
    Object.keys(block).sort().forEach(function (k) {
      var v = block[k];
      if (Array.isArray(v)) {
        rows.push('<tr><td>' + escapeHtml(k) + '</td><td><pre class="ljlk-array">' + escapeHtml(JSON.stringify(v, null, 2)) + '</pre></td></tr>');
      } else if (v !== null && typeof v === 'object') {
        rows.push('<tr><td>' + escapeHtml(k) + '</td><td><div class="ljlk-nested">' + renderKeyValue(v) + '</div></td></tr>');
      } else {
        rows.push('<tr><td>' + escapeHtml(k) + '</td><td>' + escapeHtml(String(v)) + '</td></tr>');
      }
    });
    return '<table class="ljlk-table"><tbody>' + rows.join('') + '</tbody></table>';
  }

  function renderKeyValue(obj) {
    if (obj == null || typeof obj !== 'object') return escapeHtml(String(obj));
    var rows = [];
    Object.keys(obj).forEach(function (k) {
      var v = obj[k];
      if (Array.isArray(v)) {
        rows.push('<tr><td>' + escapeHtml(k) + '</td><td><pre class="ljlk-array">' + escapeHtml(JSON.stringify(v)) + '</pre></td></tr>');
      } else if (v !== null && typeof v === 'object') {
        rows.push('<tr><td>' + escapeHtml(k) + '</td><td>' + renderKeyValue(v) + '</td></tr>');
      } else {
        rows.push('<tr><td>' + escapeHtml(k) + '</td><td>' + escapeHtml(String(v)) + '</td></tr>');
      }
    });
    return '<table class="ljlk-table ljlk-nested-table"><tbody>' + rows.join('') + '</tbody></table>';
  }

  function renderResult(horoscoop) {
    var out = [];
    var tabs = [];
    var panels = [];
    var methods = [
      { id: 'story', label: i18n.story || 'Verhaal' },
      { id: 'western', label: i18n.western || 'Westers' },
      { id: 'sidereal', label: i18n.sidereal || 'Siderisch' },
      { id: 'vedic', label: i18n.vedic || 'Vedisch' },
      { id: 'chinese', label: i18n.chinese || 'Chinees' },
      { id: 'diagnostics', label: i18n.diagnostics || 'Diagnostiek' },
    ];
    methods.forEach(function (m, i) {
      var block = horoscoop[m.id];
      var panelId = 'ljlk-tab-' + m.id;
      tabs.push('<button type="button" class="ljlk-tab-btn' + (i === 0 ? ' active' : '') + '" data-tab="' + m.id + '" aria-selected="' + (i === 0) + '" aria-controls="' + panelId + '">' + escapeHtml(m.label) + '</button>');
      if (m.id === 'story') {
        panels.push('<div id="' + panelId + '" class="ljlk-tab-panel" role="tabpanel" aria-labelledby="' + m.id + '"' + (i > 0 ? ' hidden' : '') + '>' + renderStory(horoscoop) + '</div>');
      } else {
        panels.push('<div id="' + panelId + '" class="ljlk-tab-panel" role="tabpanel" aria-labelledby="' + m.id + '"' + (i > 0 ? ' hidden' : '') + '>' + renderBlock(block, m.label) + '</div>');
      }
    });
    out.push('<div class="ljlk-tabs" role="tablist">' + tabs.join('') + '</div>');
    out.push('<div class="ljlk-tab-panels">' + panels.join('') + '</div>');
    out.push('<details class="ljlk-raw-json"><summary>' + (i18n.rawJson || 'Ruwe JSON') + '</summary><pre>' + escapeHtml(JSON.stringify(horoscoop, null, 2)) + '</pre></details>');
    return out.join('');
  }

  function getInputCompletenessSummary(h) {
    var birth = (h && h.input && h.input.birth) || {};
    var place = birth.place || {};
    var tz = birth.timezone || {};
    var provided = birth.provided || {};
    var assumptions = birth.assumptions || {};
    var diagnostics = (h && h.diagnostics) || {};
    var codes = Array.isArray(diagnostics.codes) ? diagnostics.codes : [];

    var hasDate = !!birth.date;
    var hasTime = Object.prototype.hasOwnProperty.call(provided, 'time_local')
      ? !!provided.time_local
      : !!birth.time_local;
    var hasLocation = Object.prototype.hasOwnProperty.call(provided, 'location')
      ? !!provided.location
      : (place.lat != null && place.lon != null);
    var hasTimezone = Object.prototype.hasOwnProperty.call(provided, 'timezone')
      ? !!provided.timezone
      : (!!tz.iana || tz.utc_offset_hours != null || tz.utc_offset_minutes != null);
    var timeDefaulted = !!assumptions.time_was_defaulted || codes.indexOf('USED_DEFAULT_TIME') !== -1;

    return {
      hasDate: hasDate,
      hasTime: hasTime,
      hasLocation: hasLocation,
      hasTimezone: hasTimezone,
      timeDefaulted: timeDefaulted,
      incomplete: !hasDate || !hasTime || !hasLocation || !hasTimezone || timeDefaulted,
    };
  }

  function renderStory(h) {
    var parts = [];
    var birth = (h && h.input && h.input.birth) || {};
    var place = birth.place || {};
    var tz = birth.timezone || {};
    var when = [];
    if (birth.date) when.push(birth.date);
    if (birth.time_local) when.push(String(birth.time_local).slice(0, 5));
    var where = (place.lat != null && place.lon != null) ? (Number(place.lat).toFixed(3) + ', ' + Number(place.lon).toFixed(3)) : '';
    var zone = tz.iana || (tz.utc_offset_hours != null ? ('UTC' + (tz.utc_offset_hours >= 0 ? '+' : '') + tz.utc_offset_hours) : '');
    var storyWhen = when.length
      ? formatI18n((i18n.storyWhenProvided || 'Op {when}'), { when: when.join(' ') })
      : (i18n.storyWhenFallback || 'Op het moment dat je doorgaf');
    var storyLocation = where ? formatI18n((i18n.storyLocationPart || ' op {where}'), { where: where }) : '';
    var storyZone = zone ? formatI18n((i18n.storyZonePart || ' ({zone})'), { zone: zone }) : '';
    var computedTemplate = i18n.storyComputed || '{when}{location}{zone} is je chart berekend.';
    parts.push('<p>' + escapeHtml(formatI18n(computedTemplate, { when: storyWhen, location: storyLocation, zone: storyZone })) + '</p>');
    var completeness = getInputCompletenessSummary(h);
    if (completeness.incomplete) {
      var missing = [];
      if (!completeness.hasTime || completeness.timeDefaulted) missing.push(i18n.missingExactBirthTime || 'exacte geboortetijd');
      if (!completeness.hasLocation) missing.push(i18n.missingBirthLocation || 'geboortelocatie');
      if (!completeness.hasTimezone) missing.push(i18n.missingTimezone || 'tijdzone');
      var missingLabel = missing.length ? missing.join(', ') : (i18n.missingGeneric || 'één of meer invoervelden');
      var warningTemplate = i18n.inputCompletenessWarning || 'Invoer is onvolledig of deels geschat ({missing}). Voor huizen en Ascendant zijn exacte tijd, locatie en tijdzone nodig; delen van de output kunnen daardoor ontbreken of minder precies zijn.';
      parts.push(
        '<p class="ljlk-error" role="status">' +
        escapeHtml(formatI18n(warningTemplate, { missing: missingLabel })) +
        '</p>'
      );
    }

    var western = h.western || {};
    var pl = western.placements || {};
    if (pl.Sun && pl.Sun.sign) {
      var sunHouse = pl.Sun.house ? formatI18n((i18n.storyHousePart || ', huis {house}'), { house: pl.Sun.house }) : '';
      var sunTemplate = i18n.storyWesternSun || 'In het westerse verhaal staat je Zon in {sign}{house}.';
      parts.push('<p>' + escapeHtml(formatI18n(sunTemplate, { sign: pl.Sun.sign, house: sunHouse })) + '</p>');
    }
    if (pl.Moon && pl.Moon.sign) {
      var moonHouse = pl.Moon.house ? formatI18n((i18n.storyHousePart || ', huis {house}'), { house: pl.Moon.house }) : '';
      var moonTemplate = i18n.storyWesternMoon || 'Je Maan staat in {sign}{house}.';
      parts.push('<p>' + escapeHtml(formatI18n(moonTemplate, { sign: pl.Moon.sign, house: moonHouse })) + '</p>');
    }

    var vedic = h.vedic || {};
    var pan = vedic.panchanga || {};
    if (pan && (pan.vaara || (pan.tithi && pan.tithi.index != null))) {
      var panBits = [];
      if (pan.vaara) panBits.push(formatI18n((i18n.storyVedicVaara || 'Vaara: {value}'), { value: pan.vaara }));
      if (pan.tithi && pan.tithi.index != null) panBits.push(formatI18n((i18n.storyVedicTithi || 'Tithi: {value}'), { value: pan.tithi.index }));
      if (pan.nakshatra && pan.nakshatra.index != null) panBits.push(formatI18n((i18n.storyVedicNakshatra || 'Nakshatra: {value}'), { value: pan.nakshatra.index }));
      if (pan.yoga && pan.yoga.index != null) panBits.push(formatI18n((i18n.storyVedicYoga || 'Yoga: {value}'), { value: pan.yoga.index }));
      var vedicTemplate = i18n.storyVedic || 'In de vedische kalender leest de tijd als: {bits}.';
      parts.push('<p>' + escapeHtml(formatI18n(vedicTemplate, { bits: panBits.join(', ') })) + '</p>');
    }

    var chinese = h.chinese || {};
    var b = chinese.bazi_pillars || {};
    function fmtP(p) { return (p && p.stem && p.branch) ? (p.stem + p.branch) : ''; }
    var bBits = [];
    if (fmtP(b.year)) bBits.push(formatI18n((i18n.storyBaziYear || 'jaar {value}'), { value: fmtP(b.year) }));
    if (fmtP(b.month)) bBits.push(formatI18n((i18n.storyBaziMonth || 'maand {value}'), { value: fmtP(b.month) }));
    if (fmtP(b.day)) bBits.push(formatI18n((i18n.storyBaziDay || 'dag {value}'), { value: fmtP(b.day) }));
    if (fmtP(b.hour)) bBits.push(formatI18n((i18n.storyBaziHour || 'uur {value}'), { value: fmtP(b.hour) }));
    if (bBits.length) {
      var baziTemplate = i18n.storyBazi || 'In BaZi laten de vier pilaren zien: {bits}.';
      parts.push('<p>' + escapeHtml(formatI18n(baziTemplate, { bits: bBits.join(', ') })) + '</p>');
    }

    parts.push('<p>' + escapeHtml(i18n.storyHint || 'Gebruik de andere tabbladen voor de gestructureerde details; de ruwe JSON staat hieronder.') + '</p>');
    return parts.join('');
  }

  var lastComputedHoroscoop = null;

  function doCompute() {
    var payload = getPayload();
    if (!payload.birth_date) {
      showError(get('#ljlk-result'), i18n.birthDateRequired || 'Vul geboortedatum in.');
      return;
    }
    var resultEl = get('#ljlk-result');
    resultEl.innerHTML = '<p class="ljlk-loading">' + escapeHtml(i18n.computing || 'Bezig met berekenen…') + '</p>';
    resultEl.hidden = false;

    fetch(restUrl + 'compute', fetchOptions('POST', payload))
      .then(function (r) {
        if (r.status === 429) return r.json().then(function (d) { throw new Error(d.message || i18n.rateLimit || 'Snelheidslimiet bereikt'); });
        if (r.status >= 400) return r.json().then(function (d) { throw new Error(d.message || r.statusText); });
        return r.json();
      })
      .then(function (data) {
        lastComputedHoroscoop = data;
        resultEl.innerHTML = renderResult(data);
        resultEl.hidden = false;
        // Tab switching
        getAll('.ljlk-tab-btn').forEach(function (btn) {
          btn.addEventListener('click', function () {
            var id = btn.getAttribute('data-tab');
            getAll('.ljlk-tab-btn').forEach(function (b) { b.classList.remove('active'); b.setAttribute('aria-selected', 'false'); });
            getAll('.ljlk-tab-panel').forEach(function (p) { p.hidden = true; });
            btn.classList.add('active');
            btn.setAttribute('aria-selected', 'true');
            var panel = get('#ljlk-tab-' + id);
            if (panel) { panel.hidden = false; }
          });
        });
      })
      .catch(function (err) {
        showError(resultEl, err.message || (i18n.apiUnreachable || 'De horoscoop-service is niet bereikbaar. Probeer het later opnieuw.'));
      });
  }

  function doSave() {
    var payload = getPayload();
    if (!payload.birth_date) {
      showError(get('#ljlk-result'), i18n.birthDateRequired || 'Vul geboortedatum in.');
      return;
    }
    if (lastComputedHoroscoop) {
      payload.horoscoop = lastComputedHoroscoop;
    }
    fetch(restUrl + 'save', fetchOptions('POST', payload))
      .then(function (r) {
        return r.json().then(function (data) {
          if (r.status >= 400) throw new Error(data.message || r.statusText);
          return data;
        });
      })
      .then(function () {
        var btn = get('#ljlk-save-btn');
        if (btn) {
          btn.textContent = i18n.saved || 'Opgeslagen';
          btn.disabled = true;
          setTimeout(function () { btn.textContent = i18n.save || 'Opslaan'; btn.disabled = false; }, 3000);
        }
      })
      .catch(function (err) {
        var loginIndicator = i18n.loginRequiredIndicator || 'Log in';
        if (err.message && err.message.indexOf(loginIndicator) !== -1) {
          openAuthModal(payload);
        } else {
          showError(get('#ljlk-result'), err.message);
        }
      });
  }

  function openAuthModal(savePayload) {
    var modal = get('#ljlk-auth-modal');
    var msg = get('#ljlk-auth-message');
    if (msg) msg.textContent = '';
    if (modal) {
      modal.hidden = false;
      modal.setAttribute('data-save-payload', savePayload ? JSON.stringify(savePayload) : '');
    }
  }

  function closeAuthModal() {
    var modal = get('#ljlk-auth-modal');
    if (modal) modal.hidden = true;
  }

  function onLoginSuccess() {
    closeAuthModal();
    var modal = get('#ljlk-auth-modal');
    var payloadStr = modal && modal.getAttribute('data-save-payload');
    if (payloadStr) {
      try {
        var payload = JSON.parse(payloadStr);
        if (lastComputedHoroscoop) payload.horoscoop = lastComputedHoroscoop;
        fetch(restUrl + 'save', fetchOptions('POST', payload))
          .then(function (r) { return r.json().then(function (d) { if (r.status >= 400) throw new Error(d.message); return d; }); })
          .then(function () {
            var btn = get('#ljlk-save-btn');
            if (btn) { btn.textContent = i18n.saved || 'Opgeslagen'; btn.disabled = true; setTimeout(function () { btn.textContent = i18n.save || 'Opslaan'; btn.disabled = false; }, 3000); }
          })
          .catch(function () {});
      } catch (e) {}
    }
  }

  function doRegister() {
    var email = (get('#ljlk-reg-email') && get('#ljlk-reg-email').value) || '';
    var password = (get('#ljlk-reg-password') && get('#ljlk-reg-password').value) || '';
    var msgEl = get('#ljlk-auth-message');
    if (!email) { if (msgEl) msgEl.textContent = i18n.emailRequired || 'Vul e-mail in.'; return; }
    if (password.length < 10) { if (msgEl) msgEl.textContent = (i18n.minPassword || 'Min. 10 tekens'); return; }
    if (msgEl) msgEl.textContent = '';
    fetch(restUrl + 'register', fetchOptions('POST', { email: email, password: password }))
      .then(function (r) { return r.json().then(function (d) { if (r.status >= 400) throw new Error(d.message || i18n.registerFailed || 'Registratie mislukt'); return d; }); })
      .then(function () {
        loggedIn = true;
        onLoginSuccess();
      })
      .catch(function (err) {
        if (msgEl) msgEl.textContent = err.message;
      });
  }

  function doLogin() {
    var email = (get('#ljlk-login-email') && get('#ljlk-login-email').value) || '';
    var password = (get('#ljlk-login-password') && get('#ljlk-login-password').value) || '';
    var msgEl = get('#ljlk-auth-message');
    if (!email || !password) { if (msgEl) msgEl.textContent = i18n.emailPasswordRequired || 'Vul e-mail en wachtwoord in.'; return; }
    if (msgEl) msgEl.textContent = '';
    fetch(restUrl + 'login', fetchOptions('POST', { email: email, password: password }))
      .then(function (r) { return r.json().then(function (d) { if (r.status >= 400) throw new Error(d.message || i18n.loginFailed || 'Inloggen mislukt'); return d; }); })
      .then(function () {
        loggedIn = true;
        onLoginSuccess();
      })
      .catch(function (err) {
        if (msgEl) msgEl.textContent = err.message;
      });
  }

  function loadDashboard() {
    var list = get('#ljlk-dashboard-list');
    if (!list) return;
    fetch(restUrl + 'my', fetchOptions('GET'))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var profiles = data.profiles || [];
        if (profiles.length === 0) {
          list.innerHTML = '<p>' + escapeHtml(i18n.noSavedHoroscopes || 'Geen opgeslagen horoscopen.') + '</p>';
          return;
        }
        var html = [];
        profiles.forEach(function (p) {
          html.push('<div class="ljlk-dashboard-profile">');
          html.push('<h3>' + escapeHtml(p.label || i18n.myHoroscope || 'Mijn horoscoop') + '</h3>');
          html.push('<p>' + escapeHtml(i18n.birthDateLabel || 'Geboortedatum:') + ' ' + escapeHtml(p.birth_date) + (p.birth_time ? ' ' + escapeHtml(p.birth_time) : '') + '</p>');
          (p.runs || []).forEach(function (run) {
            html.push('<div class="ljlk-dashboard-run">');
            html.push('<span>' + escapeHtml(run.computed_at) + '</span> ');
            html.push('<a href="' + restUrl + 'download/json?run_id=' + run.run_id + '" class="ljlk-dl" target="_blank" rel="noopener">' + (i18n.downloadJson || 'JSON') + '</a>');
            if (run.has_svg) html.push(' <a href="' + restUrl + 'download/wheel.svg?run_id=' + run.run_id + '" class="ljlk-dl" target="_blank" rel="noopener">' + (i18n.downloadSvg || 'SVG') + '</a>');
            if (run.has_pdf) html.push(' <a href="' + restUrl + 'download/report.pdf?run_id=' + run.run_id + '" class="ljlk-dl" target="_blank" rel="noopener">' + (i18n.downloadPdf || 'PDF') + '</a>');
            html.push('</div>');
          });
          html.push('</div>');
        });
        list.innerHTML = html.join('');
      })
      .catch(function () {
        list.innerHTML = '<p>' + escapeHtml(i18n.dashboardLoadFailed || 'Kon gegevens niet laden.') + '</p>';
      });
  }

  function initApp() {
    var accordion = get('.ljlk-accordion-btn');
    var advanced = get('.ljlk-advanced-fields');
    if (accordion && advanced) {
      accordion.addEventListener('click', function () {
        var open = advanced.hidden;
        advanced.hidden = !open;
        accordion.setAttribute('aria-expanded', open);
      });
    }
    var computeBtn = get('#ljlk-compute-btn');
    if (computeBtn) computeBtn.addEventListener('click', doCompute);
    var saveBtn = get('#ljlk-save-btn');
    if (saveBtn) saveBtn.addEventListener('click', doSave);
    var modalClose = get('.ljlk-modal-close');
    if (modalClose) modalClose.addEventListener('click', closeAuthModal);
    getAll('#ljlk-auth-modal .ljlk-tab').forEach(function (tab) {
      tab.addEventListener('click', function () {
        var t = tab.getAttribute('data-tab');
        getAll('#ljlk-auth-modal .ljlk-tab').forEach(function (x) { x.classList.remove('active'); });
        tab.classList.add('active');
        get('#ljlk-login-form').hidden = t !== 'login';
        get('#ljlk-register-form').hidden = t !== 'register';
      });
    });
    if (get('#ljlk-do-login')) get('#ljlk-do-login').addEventListener('click', doLogin);
    if (get('#ljlk-do-register')) get('#ljlk-do-register').addEventListener('click', doRegister);
  }

  function initDashboard() {
    if (get('#ljlk-horoscoop-dashboard')) loadDashboard();
  }

  if (get('#ljlk-horoscoop-app')) initApp();
  if (get('#ljlk-horoscoop-dashboard')) initDashboard();
})();
