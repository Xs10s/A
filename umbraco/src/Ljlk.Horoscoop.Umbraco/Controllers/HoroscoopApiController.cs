using System.Text.Json;
using Ljlk.Horoscoop.Umbraco.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Umbraco.Cms.Core.Security;
using Umbraco.Cms.Core.Services;
using Umbraco.Cms.Web.Common.Controllers;
using Umbraco.Cms.Web.Common.Filters;

namespace Ljlk.Horoscoop.Umbraco.Controllers;

[Route("api/ljlk/v1")]
[ApiController]
public sealed class HoroscoopApiController : UmbracoApiController
{
    private readonly IHoroscoopService _service;
    private readonly IMemberManager _memberManager;
    private readonly IMemberService _memberService;

    public HoroscoopApiController(
        IHoroscoopService service,
        IMemberManager memberManager,
        IMemberService memberService)
    {
        _service = service;
        _memberManager = memberManager;
        _memberService = memberService;
    }

    [HttpPost("compute")]
    [AllowAnonymous]
    public async Task<IActionResult> Compute([FromBody] JsonElement body, CancellationToken cancellationToken)
    {
        try
        {
            var dict = JsonElementToDictionary(body);
            var result = await _service.ComputeAsync(dict, GetClientIp(), cancellationToken).ConfigureAwait(false);
            return Ok(result);
        }
        catch (HoroscoopUserException ex)
        {
            return StatusCode(ex.Status, new { code = ex.Code, message = ex.Message });
        }
        catch (Exception)
        {
            return StatusCode(502, new { code = "api_error", message = "Horoscoop-API antwoordde met een fout." });
        }
    }

    [HttpPost("save")]
    [UmbracoMemberAuthorize]
    public async Task<IActionResult> Save([FromBody] JsonElement body, CancellationToken cancellationToken)
    {
        try
        {
            var dict = JsonElementToDictionary(body);
            var memberId = await GetMemberIdAsync().ConfigureAwait(false);
            var result = await _service.SaveAsync(dict, memberId, cancellationToken).ConfigureAwait(false);
            return Ok(result);
        }
        catch (HoroscoopUserException ex)
        {
            return StatusCode(ex.Status, new { code = ex.Code, message = ex.Message });
        }
    }

    [HttpGet("my")]
    [UmbracoMemberAuthorize]
    public async Task<IActionResult> My(CancellationToken cancellationToken)
    {
        var memberId = await GetMemberIdAsync().ConfigureAwait(false);
        if (memberId is null)
            return Unauthorized(new { code = "unauthorized", message = "Log in om je horoscopen te zien." });

        var result = await _service.ListMyAsync(memberId.Value, cancellationToken).ConfigureAwait(false);
        return Ok(result);
    }

    [HttpGet("download/json")]
    [UmbracoMemberAuthorize]
    public async Task<IActionResult> DownloadJson([FromQuery] int run_id, CancellationToken cancellationToken)
    {
        var memberId = await GetMemberIdAsync().ConfigureAwait(false);
        if (memberId is null)
            return Unauthorized();

        var json = await _service.DownloadJsonAsync(run_id, memberId.Value, cancellationToken).ConfigureAwait(false);
        if (json is null)
            return NotFound(new { code = "not_found" });

        return File(
            System.Text.Encoding.UTF8.GetBytes(JsonSerializer.Serialize(json)),
            "application/json",
            $"horoscoop-{run_id}.json");
    }

    [HttpGet("download/wheel.svg")]
    [UmbracoMemberAuthorize]
    public async Task<IActionResult> DownloadWheel([FromQuery] int run_id, CancellationToken cancellationToken)
    {
        var memberId = await GetMemberIdAsync().ConfigureAwait(false);
        if (memberId is null)
            return Unauthorized();

        var file = await _service.DownloadWheelAsync(run_id, memberId.Value, cancellationToken).ConfigureAwait(false);
        if (file is null)
            return NotFound(new { code = "not_found" });

        return File(file.Value.Content, file.Value.ContentType, file.Value.FileName);
    }

    [HttpGet("download/report.pdf")]
    [UmbracoMemberAuthorize]
    public async Task<IActionResult> DownloadReport([FromQuery] int run_id, CancellationToken cancellationToken)
    {
        var memberId = await GetMemberIdAsync().ConfigureAwait(false);
        if (memberId is null)
            return Unauthorized();

        var file = await _service.DownloadReportAsync(run_id, memberId.Value, cancellationToken).ConfigureAwait(false);
        if (file is null)
            return NotFound(new { code = "not_found" });

        return File(file.Value.Content, file.Value.ContentType, file.Value.FileName);
    }

    [HttpPost("register")]
    [AllowAnonymous]
    public async Task<IActionResult> Register([FromBody] JsonElement body, CancellationToken cancellationToken)
    {
        try
        {
            var email = body.TryGetProperty("email", out var e) ? e.GetString() : null;
            var password = body.TryGetProperty("password", out var p) ? p.GetString() : null;
            var result = await _service.RegisterAsync(email ?? string.Empty, password ?? string.Empty, GetClientIp(), cancellationToken).ConfigureAwait(false);
            return Ok(result);
        }
        catch (HoroscoopUserException ex)
        {
            return StatusCode(ex.Status, new { code = ex.Code, message = ex.Message });
        }
    }

    [HttpPost("login")]
    [AllowAnonymous]
    public async Task<IActionResult> Login([FromBody] JsonElement body, CancellationToken cancellationToken)
    {
        try
        {
            var email = body.TryGetProperty("email", out var e) ? e.GetString() : null;
            var password = body.TryGetProperty("password", out var p) ? p.GetString() : null;
            var result = await _service.LoginAsync(email ?? string.Empty, password ?? string.Empty, HttpContext, cancellationToken).ConfigureAwait(false);
            return Ok(result);
        }
        catch (HoroscoopUserException ex)
        {
            return StatusCode(ex.Status, new { code = ex.Code, message = ex.Message });
        }
    }

    private async Task<int?> GetMemberIdAsync()
    {
        var identity = await _memberManager.GetCurrentMemberAsync().ConfigureAwait(false);
        if (identity?.UserName is null)
            return null;
        var member = _memberService.GetByUsername(identity.UserName);
        return member?.Id;
    }

    private string GetClientIp()
    {
        var forwarded = HttpContext.Request.Headers["X-Forwarded-For"].FirstOrDefault();
        if (!string.IsNullOrWhiteSpace(forwarded))
            return forwarded.Split(',')[0].Trim();
        return HttpContext.Connection.RemoteIpAddress?.ToString() ?? "0.0.0.0";
    }

    private static Dictionary<string, object?> JsonElementToDictionary(JsonElement element)
    {
        var dict = new Dictionary<string, object?>(StringComparer.OrdinalIgnoreCase);
        if (element.ValueKind != JsonValueKind.Object)
            return dict;

        foreach (var prop in element.EnumerateObject())
        {
            dict[prop.Name] = prop.Value.ValueKind switch
            {
                JsonValueKind.String => prop.Value.GetString(),
                JsonValueKind.Number when prop.Value.TryGetInt32(out var i) => i,
                JsonValueKind.Number => prop.Value.GetDouble(),
                JsonValueKind.True => true,
                JsonValueKind.False => false,
                JsonValueKind.Null => null,
                JsonValueKind.Object => prop.Value,
                JsonValueKind.Array => prop.Value,
                _ => prop.Value.ToString(),
            };
        }

        return dict;
    }
}
