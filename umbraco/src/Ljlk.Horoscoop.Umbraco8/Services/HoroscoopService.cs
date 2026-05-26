using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Threading.Tasks;
using System.Web;
using System.Web.Security;
using Ljlk.Horoscoop.Core;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Umbraco.Core.Models;
using Umbraco.Web.Security;

namespace Ljlk.Horoscoop.Umbraco8.Services;

public sealed class HoroscoopService
{
    private readonly HoroscoopSettings _settings;
    private readonly HoroscoopApiClient _apiClient;
    private readonly RateLimiter _rateLimiter;
    private readonly HoroscoopRepository _repository;

    public HoroscoopService(
        HoroscoopSettings settings,
        HoroscoopApiClient apiClient,
        RateLimiter rateLimiter,
        HoroscoopRepository repository)
    {
        _settings = settings;
        _apiClient = apiClient;
        _rateLimiter = rateLimiter;
        _repository = repository;
    }

    public async Task<object> ComputeAsync(Dictionary<string, object?> body, string clientIp)
    {
        if (!_rateLimiter.TryConsume("compute:" + clientIp, _settings.RateLimitPerHour, TimeSpan.FromHours(1)))
            throw new HoroscoopUserException("rate_limit", "Te veel verzoeken. Probeer het later opnieuw.", 429);

        if (string.IsNullOrWhiteSpace(_settings.ApiBaseUrl))
            throw new HoroscoopUserException("config", "API is niet geconfigureerd.", 503);

        var birthDate = GetString(body, "birth_date");
        if (!PayloadValidator.ValidateBirthDate(birthDate))
            throw new HoroscoopUserException("invalid_input", "Ongeldige geboortedatum (gebruik JJJJ-MM-DD).", 400);

        var birthTime = GetString(body, "birth_time");
        if (!PayloadValidator.ValidateBirthTime(birthTime))
            throw new HoroscoopUserException("invalid_input", "Ongeldige geboortetijd.", 400);

        var payload = PayloadSanitizer.SanitizeForApi(body);
        payload["birth_date"] = birthDate!.Substring(0, 10);
        return await _apiClient.ComputeAsync(_settings.ApiBaseUrl, payload).ConfigureAwait(false) ?? new { };
    }

    public async Task<object> SaveAsync(Dictionary<string, object?> body, int? memberId)
    {
        if (memberId is null or <= 0)
            throw new HoroscoopUserException("unauthorized", "Log in om op te slaan.", 401);

        var birthDate = GetString(body, "birth_date");
        if (!PayloadValidator.ValidateBirthDate(birthDate))
            throw new HoroscoopUserException("invalid_input", "Ongeldige geboortedatum.", 400);

        var apiPayload = PayloadSanitizer.SanitizeForApi(body);
        apiPayload["birth_date"] = birthDate!.Substring(0, 10);
        var hashPayload = PayloadSanitizer.ToHashPayload(body, apiPayload);
        var inputHash = InputHasher.InputHash(hashPayload);

        var profileId = _repository.GetFirstProfileId(memberId.Value);
        if (profileId is null)
        {
            if (_repository.CountProfiles(memberId.Value) >= Math.Max(1, _settings.MaxSavesPerUser))
                throw new HoroscoopUserException("limit", "Maximum aantal horoscopen bereikt.", 403);

            profileId = _repository.CreateProfile(new
            {
                memberId = memberId.Value,
                label = Truncate(GetString(body, "label") ?? "Mijn horoscoop", 100),
                birthDate = DateTime.ParseExact(apiPayload["birth_date"]!.ToString()!, "yyyy-MM-dd", CultureInfo.InvariantCulture),
                birthTime = ParseTime(GetString(body, "birth_time")),
                latitude = apiPayload.ContainsKey("lat") ? apiPayload["lat"] : null,
                longitude = apiPayload.ContainsKey("lon") ? apiPayload["lon"] : null,
                timezoneIana = apiPayload.ContainsKey("timezone_iana") ? apiPayload["timezone_iana"] : null,
                utcOffsetMinutes = apiPayload.ContainsKey("utc_offset_minutes") ? apiPayload["utc_offset_minutes"] : null,
                settingsJson = apiPayload.ContainsKey("settings") ? JsonConvert.SerializeObject(apiPayload["settings"]) : null,
                createdAt = DateTime.UtcNow,
            });
        }

        var existing = _repository.GetRunByHash(profileId.Value, inputHash);
        if (existing != null)
        {
            return new
            {
                profile_id = profileId.Value,
                run_id = (int)existing.id,
                computed_at = ((DateTime)existing.computedAt).ToString("o"),
            };
        }

        object? horoscoop = body.ContainsKey("horoscoop") ? body["horoscoop"] : null;
        if (horoscoop is null && !string.IsNullOrWhiteSpace(_settings.ApiBaseUrl))
            horoscoop = await _apiClient.ComputeAsync(_settings.ApiBaseUrl, apiPayload).ConfigureAwait(false);

        if (horoscoop is null)
            throw new HoroscoopUserException("invalid_input", "Geen horoscoop om op te slaan. Bereken eerst een horoscoop.", 400);

        if (_repository.CountRunsForMember(memberId.Value) >= Math.Max(1, _settings.MaxSavesPerUser) * 5)
            throw new HoroscoopUserException("limit", "Maximum aantal runs bereikt.", 403);

        string? wheelSvg = null;
        byte[]? reportPdf = null;
        if (_settings.CacheSvgPdf && !string.IsNullOrWhiteSpace(_settings.ApiBaseUrl))
        {
            try
            {
                wheelSvg = await _apiClient.RenderWheelSvgAsync(_settings.ApiBaseUrl, new { engine_json = horoscoop }).ConfigureAwait(false);
            }
            catch { /* optional */ }

            try
            {
                var pdf = await _apiClient.RenderReportPdfAsync(_settings.ApiBaseUrl, new { engine_json = horoscoop }).ConfigureAwait(false);
                if (pdf.Length < 5 * 1024 * 1024)
                    reportPdf = pdf;
            }
            catch { /* optional */ }
        }

        var json = horoscoop is string s ? s : JsonConvert.SerializeObject(horoscoop);
        var runId = _repository.InsertRun(new
        {
            profileId = profileId.Value,
            inputHash,
            engineVersion = (string?)null,
            computedAt = DateTime.UtcNow,
            horoscoopJson = json,
            wheelSvg,
            reportPdf,
            reportPdfUrl = (string?)null,
        });

        return new
        {
            profile_id = profileId.Value,
            run_id = runId,
            computed_at = DateTime.UtcNow.ToString("o"),
        };
    }

    public object ListMy(int memberId)
    {
        var profiles = _repository.ListProfiles(memberId);
        var result = new List<object>();
        foreach (var p in profiles)
        {
            var runs = _repository.ListRuns((int)p.id);
            result.Add(new
            {
                profile_id = (int)p.id,
                label = (string?)p.label,
                birth_date = ((DateTime)p.birthDate).ToString("yyyy-MM-dd"),
                birth_time = p.birthTime != null ? ((TimeSpan)p.birthTime).ToString(@"hh\:mm\:ss") : null,
                created_at = ((DateTime)p.createdAt).ToString("o"),
                runs = runs.Select(r => new
                {
                    run_id = (int)r.id,
                    computed_at = ((DateTime)r.computedAt).ToString("o"),
                    has_svg = r.wheelSvg != null,
                    has_pdf = r.reportPdf != null || r.reportPdfUrl != null,
                }),
            });
        }

        return new { profiles = result };
    }

    public object? DownloadJson(int runId, int memberId)
    {
        var run = _repository.GetRunForMember(runId, memberId);
        if (run is null)
            return null;
        return JsonConvert.DeserializeObject((string)run.horoscoopJson);
    }

    public (byte[] Content, string ContentType, string FileName)? DownloadWheel(int runId, int memberId)
    {
        var run = _repository.GetRunForMember(runId, memberId);
        if (run is null || run.wheelSvg is null)
            return null;
        return (System.Text.Encoding.UTF8.GetBytes((string)run.wheelSvg), "image/svg+xml", "wheel-" + runId + ".svg");
    }

    public (byte[] Content, string ContentType, string FileName)? DownloadReport(int runId, int memberId)
    {
        var run = _repository.GetRunForMember(runId, memberId);
        if (run is null || run.reportPdf is null)
            return null;
        return ((byte[])run.reportPdf, "application/pdf", "report-" + runId + ".pdf");
    }

    public object Register(string email, string password, string clientIp)
    {
        if (!_rateLimiter.TryConsume("register:" + clientIp, 5, TimeSpan.FromHours(1)))
            throw new HoroscoopUserException("throttle", "Te veel registratiepogingen. Probeer het later opnieuw.", 429);

        if (string.IsNullOrWhiteSpace(email) || !email.Contains("@"))
            throw new HoroscoopUserException("invalid_email", "Ongeldig e-mailadres.", 400);
        if (password.Length < 10)
            throw new HoroscoopUserException("weak_password", "Wachtwoord moet minimaal 10 tekens zijn.", 400);

        if (Members.GetByEmail(email) != null)
            throw new HoroscoopUserException("email_exists", "Dit e-mailadres is al geregistreerd. Log in.", 400);

        var username = email.Replace('@', '_').Replace('.', '_');
        var member = Members.RegisterMember(username, email, password, "Member");
        if (member is null)
            throw new HoroscoopUserException("creation_failed", "Registratie mislukt.", 400);

        Members.Login(member.Username, password);
        return new { success = true, member_id = member.Id };
    }

    public object Login(string email, string password)
    {
        if (string.IsNullOrWhiteSpace(email) || !email.Contains("@"))
            throw new HoroscoopUserException("invalid_email", "Ongeldig e-mailadres.", 400);

        var member = Members.GetByEmail(email);
        if (member is null || !Members.Login(member.Username, password))
            throw new HoroscoopUserException("invalid_credentials", "Onjuist e-mailadres of wachtwoord.", 401);

        return new { success = true, member_id = member.Id };
    }

    private static string? GetString(Dictionary<string, object?> dict, string key)
        => dict.TryGetValue(key, out var value) ? value?.ToString() : null;

    private static TimeSpan? ParseTime(string? time)
        => string.IsNullOrWhiteSpace(time) ? null : TimeSpan.TryParse(time, out var ts) ? ts : (TimeSpan?)null;

    private static string Truncate(string value, int max)
        => value.Length <= max ? value : value.Substring(0, max);
}

public sealed class HoroscoopUserException : Exception
{
    public HoroscoopUserException(string code, string message, int status)
        : base(message)
    {
        Code = code;
        Status = status;
    }

    public string Code { get; }
    public int Status { get; }
}
