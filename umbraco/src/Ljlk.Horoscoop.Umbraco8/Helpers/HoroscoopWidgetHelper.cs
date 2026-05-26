using System.Web;
using Umbraco.Web.Security;

namespace Ljlk.Horoscoop.Umbraco8.Helpers;

/// <summary>Razor/HTML helpers for embedding the horoscope widget in Umbraco 8 templates.</summary>
public static class HoroscoopWidgetHelper
{
    public static IHtmlString RenderApp(string staticBase = "/ljlk-horoscoop/")
    {
        var loggedIn = Members.IsLoggedIn();
        var config = BuildConfigScript(staticBase, loggedIn, includeDashboardStrings: false);
        return new HtmlString(config + ReadPartial("AppMarkup"));
    }

    public static IHtmlString RenderDashboard(string staticBase = "/ljlk-horoscoop/")
    {
        if (!Members.IsLoggedIn())
            return new HtmlString("<p class=\"ljlk-dashboard-guest\">Log in om je opgeslagen horoscopen te zien.</p>");

        var config = BuildConfigScript(staticBase, loggedIn: true, includeDashboardStrings: true);
        return new HtmlString(config + ReadPartial("DashboardMarkup"));
    }

    private static string BuildConfigScript(string staticBase, bool loggedIn, bool includeDashboardStrings)
    {
        var i18n = includeDashboardStrings
            ? @"noSavedHoroscopes: ""Geen opgeslagen horoscopen."", myHoroscope: ""Mijn horoscoop"",
               birthDateLabel: ""Geboortedatum:"", downloadJson: ""JSON downloaden"",
               downloadSvg: ""Wiel (SVG)"", downloadPdf: ""Rapport (PDF)"",
               dashboardLoadFailed: ""Kon gegevens niet laden."""
            : @"compute: ""Berekenen"", save: ""Opslaan"", saved: ""Opgeslagen"",
               birthDateRequired: ""Vul geboortedatum in."", computing: ""Bezig met berekenenù"",
               rateLimit: ""Snelheidslimiet bereikt"", error: ""Fout"",
               apiUnreachable: ""De horoscoop-service is niet bereikbaar. Probeer het later opnieuw."",
               loginRequiredIndicator: ""Log in"",
               western: ""Westers"", sidereal: ""Siderisch"", vedic: ""Vedisch"", chinese: ""Chinees"",
               diagnostics: ""Diagnostiek"", rawJson: ""Ruwe JSON"", story: ""Verhaal"",
               storyHint: ""Gebruik de andere tabbladen voor de gestructureerde details; de ruwe JSON staat hieronder."",
               registerFailed: ""Registratie mislukt"", loginFailed: ""Inloggen mislukt"",
               emailRequired: ""Vul e-mail in."", emailPasswordRequired: ""Vul e-mail en wachtwoord in."",
               minPassword: ""Min. 10 tekens""";

        return $@"<link rel=""stylesheet"" href=""{staticBase}app.css"" />
<script>
window.ljlkHoroscoop = {{
  restUrl: ""/api/ljlk/v1/"",
  loggedIn: {(loggedIn ? "true" : "false")},
  i18n: {{ {i18n} }}
}};
</script>
<script src=""{staticBase}app.js""></script>";
    }

    private static string ReadPartial(string name)
    {
        switch (name)
        {
        case "AppMarkup":
            return @"<div id=""ljlk-horoscoop-app"" class=""ljlk-horoscoop-app"">
  <div class=""ljlk-horoscoop-form"">
    <label for=""ljlk-birth-date"">Geboortedatum <span class=""required"">*</span></label>
    <input type=""date"" id=""ljlk-birth-date"" name=""birth_date"" required />
    <div class=""ljlk-advanced-toggle"">
      <button type=""button"" class=""ljlk-accordion-btn"" aria-expanded=""false"">Geavanceerd</button>
      <div class=""ljlk-advanced-fields"" hidden>
        <label for=""ljlk-birth-time"">Geboortetijd</label>
        <input type=""time"" id=""ljlk-birth-time"" name=""birth_time"" step=""1"" />
        <label for=""ljlk-latitude"">Breedtegraad</label>
        <input type=""number"" id=""ljlk-latitude"" name=""latitude"" step=""any"" placeholder=""52.0"" />
        <label for=""ljlk-longitude"">Lengtegraad</label>
        <input type=""number"" id=""ljlk-longitude"" name=""longitude"" step=""any"" placeholder=""5.0"" />
        <label for=""ljlk-timezone"">Tijdzone (IANA)</label>
        <input type=""text"" id=""ljlk-timezone"" name=""timezone_iana"" placeholder=""Europe/Amsterdam"" />
        <label for=""ljlk-utc-offset"">UTC-offset (minuten)</label>
        <input type=""number"" id=""ljlk-utc-offset"" name=""utc_offset_minutes"" placeholder=""60"" />
      </div>
    </div>
    <div class=""ljlk-actions"">
      <button type=""button"" id=""ljlk-compute-btn"" class=""ljlk-btn ljlk-btn-primary"">Berekenen</button>
      <button type=""button"" id=""ljlk-save-btn"" class=""ljlk-btn ljlk-btn-secondary"">Opslaan</button>
    </div>
  </div>
  <div id=""ljlk-result"" class=""ljlk-result"" aria-live=""polite""></div>
  <div id=""ljlk-auth-modal"" class=""ljlk-modal"" role=""dialog"" aria-labelledby=""ljlk-auth-title"" aria-modal=""true"" hidden>
    <div class=""ljlk-modal-content"">
      <h2 id=""ljlk-auth-title"">Opslaan</h2>
      <p class=""ljlk-auth-intro"">Log in of maak een account aan om je horoscoop op te slaan.</p>
      <div id=""ljlk-auth-tabs"">
        <button type=""button"" class=""ljlk-tab active"" data-tab=""login"">Inloggen</button>
        <button type=""button"" class=""ljlk-tab"" data-tab=""register"">Registreren</button>
      </div>
      <div id=""ljlk-login-form"" class=""ljlk-auth-form"">
        <label for=""ljlk-login-email"">E-mail</label>
        <input type=""email"" id=""ljlk-login-email"" />
        <label for=""ljlk-login-password"">Wachtwoord</label>
        <input type=""password"" id=""ljlk-login-password"" />
        <button type=""button"" id=""ljlk-do-login"" class=""ljlk-btn ljlk-btn-primary"">Inloggen</button>
      </div>
      <div id=""ljlk-register-form"" class=""ljlk-auth-form"" hidden>
        <label for=""ljlk-reg-email"">E-mail</label>
        <input type=""email"" id=""ljlk-reg-email"" />
        <label for=""ljlk-reg-password"">Wachtwoord <span class=""ljlk-hint"">(Min. 10 tekens)</span></label>
        <input type=""password"" id=""ljlk-reg-password"" minlength=""10"" />
        <button type=""button"" id=""ljlk-do-register"" class=""ljlk-btn ljlk-btn-primary"">Registreren</button>
      </div>
      <div id=""ljlk-auth-message"" class=""ljlk-auth-message"" role=""alert""></div>
      <button type=""button"" class=""ljlk-modal-close"" aria-label=""Sluiten"">&times;</button>
    </div>
  </div>
</div>";
        case "DashboardMarkup":
            return @"<div id=""ljlk-horoscoop-dashboard"" class=""ljlk-horoscoop-dashboard"">
  <h2>Mijn horoscopen</h2>
  <div id=""ljlk-dashboard-list""></div>
</div>";
        default:
            return string.Empty;
        }
    }
}
