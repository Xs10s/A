using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Web.Http;
using Ljlk.Horoscoop.Umbraco8.Services;
using Newtonsoft.Json.Linq;
using Umbraco.Web;
using Umbraco.Web.Mvc;
using Umbraco.Web.WebApi;

namespace Ljlk.Horoscoop.Umbraco8.Controllers;

[RoutePrefix("api/ljlk/v1")]
public sealed class HoroscoopApiController : UmbracoApiController
{
    private readonly HoroscoopService _service;

    public HoroscoopApiController(HoroscoopService service)
    {
        _service = service;
    }

    [HttpPost]
    [Route("compute")]
    public async System.Threading.Tasks.Task<HttpResponseMessage> Compute([FromBody] JObject body)
    {
        try
        {
            var dict = JObjectToDictionary(body);
            var result = await _service.ComputeAsync(dict, GetClientIp()).ConfigureAwait(false);
            return Request.CreateResponse(HttpStatusCode.OK, result);
        }
        catch (HoroscoopUserException ex)
        {
            return Request.CreateResponse((HttpStatusCode)ex.Status, new { code = ex.Code, message = ex.Message });
        }
        catch
        {
            return Request.CreateResponse(HttpStatusCode.BadGateway, new { code = "api_error", message = "Horoscoop-API antwoordde met een fout." });
        }
    }

    [HttpPost]
    [Route("save")]
    [MemberAuthorize]
    public async System.Threading.Tasks.Task<HttpResponseMessage> Save([FromBody] JObject body)
    {
        try
        {
            var dict = JObjectToDictionary(body);
            var member = Members.GetCurrentMember();
            var result = await _service.SaveAsync(dict, member?.Id).ConfigureAwait(false);
            return Request.CreateResponse(HttpStatusCode.OK, result);
        }
        catch (HoroscoopUserException ex)
        {
            return Request.CreateResponse((HttpStatusCode)ex.Status, new { code = ex.Code, message = ex.Message });
        }
    }

    [HttpGet]
    [Route("my")]
    [MemberAuthorize]
    public HttpResponseMessage My()
    {
        var member = Members.GetCurrentMember();
        if (member is null)
            return Request.CreateResponse(HttpStatusCode.Unauthorized, new { code = "unauthorized" });
        return Request.CreateResponse(HttpStatusCode.OK, _service.ListMy(member.Id));
    }

    [HttpGet]
    [Route("download/json")]
    [MemberAuthorize]
    public HttpResponseMessage DownloadJson(int run_id)
    {
        var member = Members.GetCurrentMember();
        if (member is null)
            return Request.CreateResponse(HttpStatusCode.Unauthorized);
        var json = _service.DownloadJson(run_id, member.Id);
        if (json is null)
            return Request.CreateResponse(HttpStatusCode.NotFound, new { code = "not_found" });
        return Request.CreateResponse(HttpStatusCode.OK, json);
    }

    [HttpGet]
    [Route("download/wheel.svg")]
    [MemberAuthorize]
    public HttpResponseMessage DownloadWheel(int run_id)
    {
        var member = Members.GetCurrentMember();
        if (member is null)
            return Request.CreateResponse(HttpStatusCode.Unauthorized);
        var file = _service.DownloadWheel(run_id, member.Id);
        if (file is null)
            return Request.CreateResponse(HttpStatusCode.NotFound, new { code = "not_found" });
        var response = Request.CreateResponse(HttpStatusCode.OK);
        response.Content = new ByteArrayContent(file.Value.Content);
        response.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(file.Value.ContentType);
        return response;
    }

    [HttpGet]
    [Route("download/report.pdf")]
    [MemberAuthorize]
    public HttpResponseMessage DownloadReport(int run_id)
    {
        var member = Members.GetCurrentMember();
        if (member is null)
            return Request.CreateResponse(HttpStatusCode.Unauthorized);
        var file = _service.DownloadReport(run_id, member.Id);
        if (file is null)
            return Request.CreateResponse(HttpStatusCode.NotFound, new { code = "not_found" });
        var response = Request.CreateResponse(HttpStatusCode.OK);
        response.Content = new ByteArrayContent(file.Value.Content);
        response.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(file.Value.ContentType);
        return response;
    }

    [HttpPost]
    [Route("register")]
    public HttpResponseMessage Register([FromBody] JObject body)
    {
        try
        {
            var email = body.Value<string>("email") ?? string.Empty;
            var password = body.Value<string>("password") ?? string.Empty;
            var result = _service.Register(email, password, GetClientIp());
            return Request.CreateResponse(HttpStatusCode.OK, result);
        }
        catch (HoroscoopUserException ex)
        {
            return Request.CreateResponse((HttpStatusCode)ex.Status, new { code = ex.Code, message = ex.Message });
        }
    }

    [HttpPost]
    [Route("login")]
    public HttpResponseMessage Login([FromBody] JObject body)
    {
        try
        {
            var email = body.Value<string>("email") ?? string.Empty;
            var password = body.Value<string>("password") ?? string.Empty;
            var result = _service.Login(email, password);
            return Request.CreateResponse(HttpStatusCode.OK, result);
        }
        catch (HoroscoopUserException ex)
        {
            return Request.CreateResponse((HttpStatusCode)ex.Status, new { code = ex.Code, message = ex.Message });
        }
    }

    private string GetClientIp()
    {
        var ctx = System.Web.HttpContext.Current;
        if (ctx?.Request.Headers["X-Forwarded-For"] is string forwarded && !string.IsNullOrWhiteSpace(forwarded))
            return forwarded.Split(',')[0].Trim();
        return ctx?.Request.UserHostAddress ?? "0.0.0.0";
    }

    private static Dictionary<string, object?> JObjectToDictionary(JObject? body)
    {
        var dict = new Dictionary<string, object?>(StringComparer.OrdinalIgnoreCase);
        if (body is null)
            return dict;
        foreach (var prop in body.Properties())
            dict[prop.Name] = prop.Value.Type == JTokenType.Object || prop.Value.Type == JTokenType.Array
                ? prop.Value
                : ((JValue)prop.Value).Value;
        return dict;
    }
}
