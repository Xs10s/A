using System.Globalization;
using System.Text.Json;
using Ljlk.Horoscoop.Core;
using Ljlk.Horoscoop.Umbraco.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Options;
using Newtonsoft.Json.Linq;
using Umbraco.Cms.Core.Models;
using Umbraco.Cms.Core.Security;
using Umbraco.Cms.Core.Services;
using Umbraco.Cms.Web.Common.Security;

namespace Ljlk.Horoscoop.Umbraco.Services;

public sealed class HoroscoopService : IHoroscoopService
{
    private readonly HoroscoopSettings _settings;
    private readonly HoroscoopApiClient _apiClient;
    private readonly RateLimiter _rateLimiter;
    private readonly IHoroscoopRepository _repository;
    private readonly IMemberService _memberService;
    private readonly IMemberManager _memberManager;
    private readonly IMemberSignInManager _memberSignInManager;

    public HoroscoopService(
        IOptions<HoroscoopSettings> settings,
        HoroscoopApiClient apiClient,
        RateLimiter rateLimiter,
        IHoroscoopRepository repository,
        IMemberService memberService,
        IMemberManager memberManager,
        IMemberSignInManager memberSignInManager)
    {
        _settings = settings.Value;
        _apiClient = apiClient;
        _rateLimiter = rateLimiter;
        _repository = repository;
        _memberService = memberService;
        _memberManager = memberManager;
        _memberSignInManager = memberSignInManager;
    }

    public async Task<object> ComputeAsync(
        IReadOnlyDictionary<string, object?> body,
        string clientIp,
        CancellationToken cancellationToken = default)
    {
        if (!_rateLimiter.TryConsume($"compute:{clientIp}", _settings.RateLimitPerHour, TimeSpan.FromHours(1)))
            throw new HoroscoopUserException("rate_limit", "Te veel verzoeken. Probeer het later opnieuw.", 429);

        EnsureApiConfigured();
        var birthDate = GetString(body, "birth_date");
        if (!PayloadValidator.ValidateBirthDate(birthDate))
            throw new HoroscoopUserException("invalid_input", "Ongeldige geboortedatum (gebruik JJJJ-MM-DD).", 400);

        var birthTime = GetString(body, "birth_time");
        if (!PayloadValidator.ValidateBirthTime(birthTime))
            throw new HoroscoopUserException("invalid_input", "Ongeldige geboortetijd.", 400);

        var payload = PayloadSanitizer.SanitizeForApi(body);
        payload["birth_date"] = birthDate!.Substring(0, 10);

        return await _apiClient.ComputeAsync(_settings.ApiBaseUrl, payload, cancellationToken).ConfigureAwait(false)
               ?? new { };
    }

    public async Task<object> SaveAsync(
        IReadOnlyDictionary<string, object?> body,
        int? memberId,
        CancellationToken cancellationToken = default)
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

        var profileId = await _repository.GetFirstProfileIdAsync(memberId.Value, cancellationToken).ConfigureAwait(false);
        if (profileId is null)
        {
            var count = await _repository.CountProfilesAsync(memberId.Value, cancellationToken).ConfigureAwait(false);
            if (count >= Math.Max(1, _settings.MaxSavesPerUser))
                throw new HoroscoopUserException("limit", "Maximum aantal horoscopen bereikt.", 403);

            profileId = await _repository.CreateProfileAsync(new HoroscopeProfile
            {
                MemberId = memberId.Value,
                Label = Truncate(GetString(body, "label") ?? "Mijn horoscoop", 100),
                BirthDate = DateTime.ParseExact(apiPayload["birth_date"]!.ToString()!, "yyyy-MM-dd", CultureInfo.InvariantCulture),
                BirthTime = ParseTime(apiPayload.TryGetValue("birth_time_local", out var bt) ? bt?.ToString() : null),
                Latitude = apiPayload["lat"] as double? ?? (apiPayload.TryGetValue("lat", out var latObj) && latObj is double lat ? lat : null),
                Longitude = apiPayload["lon"] as double? ?? (apiPayload.TryGetValue("lon", out var lonObj) && lonObj is double lon ? lon : null),
                TimezoneIana = apiPayload.TryGetValue("timezone_iana", out var tz) ? tz?.ToString() : null,
                UtcOffsetMinutes = apiPayload["utc_offset_minutes"] is int um ? (short?)um : null,
                SettingsJson = apiPayload.TryGetValue("settings", out var st) && st != null
                    ? JsonSerializer.Serialize(st)
                    : null,
                CreatedAt = DateTime.UtcNow,
            }, cancellationToken).ConfigureAwait(false);
        }

        var existing = await _repository.GetRunByHashAsync(profileId.Value, inputHash, cancellationToken).ConfigureAwait(false);
        if (existing != null)
        {
            return new
            {
                profile_id = profileId.Value,
                run_id = existing.Id,
                computed_at = existing.ComputedAt.ToString("o"),
            };
        }

        object? horoscoop = null;
        if (body.TryGetValue("horoscoop", out var precomputed))
            horoscoop = precomputed;

        if (horoscoop is null && !string.IsNullOrWhiteSpace(_settings.ApiBaseUrl))
            horoscoop = await _apiClient.ComputeAsync(_settings.ApiBaseUrl, apiPayload, cancellationToken).ConfigureAwait(false);

        if (horoscoop is null)
            throw new HoroscoopUserException("invalid_input", "Geen horoscoop om op te slaan. Bereken eerst een horoscoop.", 400);

        var runCount = await _repository.CountRunsForMemberAsync(memberId.Value, cancellationToken).ConfigureAwait(false);
        if (runCount >= Math.Max(1, _settings.MaxSavesPerUser) * 5)
            throw new HoroscoopUserException("limit", "Maximum aantal runs bereikt.", 403);

        string? wheelSvg = null;
        byte[]? reportPdf = null;
        if (_settings.CacheSvgPdf && !string.IsNullOrWhiteSpace(_settings.ApiBaseUrl))
        {
            try
            {
                wheelSvg = await _apiClient.RenderWheelSvgAsync(
                    _settings.ApiBaseUrl,
                    new { engine_json = horoscoop },
                    cancellationToken).ConfigureAwait(false);
            }
            catch
            {
                // optional cache
            }

            try
            {
                var pdf = await _apiClient.RenderReportPdfAsync(
                    _settings.ApiBaseUrl,
                    new { engine_json = horoscoop },
                    cancellationToken).ConfigureAwait(false);
                if (pdf.Length < 5 * 1024 * 1024)
                    reportPdf = pdf;
            }
            catch
            {
                // optional cache
            }
        }

        var json = horoscoop is string s ? s : JsonSerializer.Serialize(horoscoop);
        var runId = await _repository.InsertRunAsync(new HoroscopeRun
        {
            ProfileId = profileId.Value,
            InputHash = inputHash,
            ComputedAt = DateTime.UtcNow,
            HoroscoopJson = json,
            WheelSvg = wheelSvg,
            ReportPdf = reportPdf,
        }, cancellationToken).ConfigureAwait(false);

        return new
        {
            profile_id = profileId.Value,
            run_id = runId,
            computed_at = DateTime.UtcNow.ToString("o"),
        };
    }

    public async Task<object> ListMyAsync(int memberId, CancellationToken cancellationToken = default)
    {
        var profiles = await _repository.ListProfilesAsync(memberId, cancellationToken).ConfigureAwait(false);
        var result = new List<object>();
        foreach (var p in profiles)
        {
            var runs = await _repository.ListRunsAsync(p.Id, cancellationToken).ConfigureAwait(false);
            result.Add(new
            {
                profile_id = p.Id,
                label = p.Label,
                birth_date = p.BirthDate.ToString("yyyy-MM-dd"),
                birth_time = p.BirthTime?.ToString(@"hh\:mm\:ss"),
                created_at = p.CreatedAt.ToString("o"),
                runs = runs.Select(r => new
                {
                    run_id = r.Id,
                    computed_at = r.ComputedAt.ToString("o"),
                    has_svg = !string.IsNullOrEmpty(r.WheelSvg),
                    has_pdf = r.ReportPdf is { Length: > 0 } || !string.IsNullOrEmpty(r.ReportPdfUrl),
                }),
            });
        }

        return new { profiles = result };
    }

    public async Task<object?> DownloadJsonAsync(int runId, int memberId, CancellationToken cancellationToken = default)
    {
        var run = await _repository.GetRunForMemberAsync(runId, memberId, cancellationToken).ConfigureAwait(false);
        if (run is null)
            return null;
        return JsonSerializer.Deserialize<object>(run.HoroscoopJson);
    }

    public async Task<(byte[] Content, string ContentType, string FileName)?> DownloadWheelAsync(
        int runId,
        int memberId,
        CancellationToken cancellationToken = default)
    {
        var run = await _repository.GetRunForMemberAsync(runId, memberId, cancellationToken).ConfigureAwait(false);
        if (run is null || string.IsNullOrEmpty(run.WheelSvg))
            return null;
        return (System.Text.Encoding.UTF8.GetBytes(run.WheelSvg), "image/svg+xml", $"wheel-{runId}.svg");
    }

    public async Task<(byte[] Content, string ContentType, string FileName)?> DownloadReportAsync(
        int runId,
        int memberId,
        CancellationToken cancellationToken = default)
    {
        var run = await _repository.GetRunForMemberAsync(runId, memberId, cancellationToken).ConfigureAwait(false);
        if (run is null)
            return null;
        if (run.ReportPdf is { Length: > 0 })
            return (run.ReportPdf, "application/pdf", $"report-{runId}.pdf");
        return null;
    }

    public async Task<object> RegisterAsync(
        string email,
        string password,
        string clientIp,
        CancellationToken cancellationToken = default)
    {
        if (!_rateLimiter.TryConsume($"register:{clientIp}", 5, TimeSpan.FromHours(1)))
            throw new HoroscoopUserException("throttle", "Te veel registratiepogingen. Probeer het later opnieuw.", 429);

        if (string.IsNullOrWhiteSpace(email) || !email.Contains('@'))
            throw new HoroscoopUserException("invalid_email", "Ongeldig e-mailadres.", 400);
        if (password.Length < 10)
            throw new HoroscoopUserException("weak_password", "Wachtwoord moet minimaal 10 tekens zijn.", 400);

        if (_memberService.GetByEmail(email) != null)
            throw new HoroscoopUserException("email_exists", "Dit e-mailadres is al geregistreerd. Log in.", 400);

        var username = SanitizeUsername(email);
        var identityUser = MemberIdentityUser.CreateNew(username, email, "Member", true);
        var createResult = await _memberManager.CreateAsync(identityUser, password).ConfigureAwait(false);
        if (!createResult.Succeeded)
        {
            var message = string.Join("; ", createResult.Errors.Select(e => e.Description));
            throw new HoroscoopUserException("creation_failed", message, 400);
        }

        await _memberSignInManager.PasswordSignInAsync(identityUser.UserName!, password, true, false).ConfigureAwait(false);
        var member = _memberService.GetByEmail(email);
        return new { success = true, member_id = member?.Id };
    }

    public async Task<object> LoginAsync(
        string email,
        string password,
        HttpContext httpContext,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(email) || !email.Contains('@'))
            throw new HoroscoopUserException("invalid_email", "Ongeldig e-mailadres.", 400);

        var member = _memberService.GetByEmail(email);
        if (member is null)
            throw new HoroscoopUserException("invalid_credentials", "Onjuist e-mailadres of wachtwoord.", 401);

        var identityUser = await _memberManager.FindByEmailAsync(email).ConfigureAwait(false);
        if (identityUser is null)
            throw new HoroscoopUserException("invalid_credentials", "Onjuist e-mailadres of wachtwoord.", 401);

        var signIn = await _memberSignInManager.PasswordSignInAsync(identityUser.UserName!, password, true, false).ConfigureAwait(false);
        if (!signIn.Succeeded)
            throw new HoroscoopUserException("invalid_credentials", "Onjuist e-mailadres of wachtwoord.", 401);

        return new { success = true, member_id = member.Id };
    }

    private void EnsureApiConfigured()
    {
        if (string.IsNullOrWhiteSpace(_settings.ApiBaseUrl))
            throw new HoroscoopUserException("config", "API is niet geconfigureerd.", 503);
    }

    private static string? GetString(IReadOnlyDictionary<string, object?> dict, string key)
    {
        if (!dict.TryGetValue(key, out var value) || value is null)
            return null;
        if (value is JsonElement el)
            return el.ValueKind == JsonValueKind.String ? el.GetString() : el.ToString();
        return value.ToString();
    }

    private static TimeSpan? ParseTime(string? time)
    {
        if (string.IsNullOrWhiteSpace(time))
            return null;
        return TimeSpan.TryParse(time, CultureInfo.InvariantCulture, out var ts) ? ts : null;
    }

    private static string Truncate(string value, int max)
        => value.Length <= max ? value : value.Substring(0, max);

    private static string SanitizeUsername(string email)
    {
        var username = email
            .Replace('@', '_')
            .Replace('.', '_')
            .Replace('+', '_')
            .Replace(' ', '_');
        return username.Length < 2 ? $"user_{Random.Shared.Next(10000, 99999)}" : username;
    }
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
