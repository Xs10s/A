using System;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace Ljlk.Horoscoop.Core;

public sealed class HoroscoopApiClient
{
    private static readonly HttpClient SharedClient = new HttpClient
    {
        Timeout = TimeSpan.FromSeconds(60),
    };

    public async Task<object?> ComputeAsync(
        string baseUrl,
        object payload,
        CancellationToken cancellationToken = default)
    {
        var url = $"{baseUrl.TrimEnd('/')}/api/horoscoop";
        var json = JsonConvert.SerializeObject(payload);
        using var request = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = new StringContent(json, Encoding.UTF8, "application/json"),
        };
        using var response = await SharedClient.SendAsync(request, cancellationToken).ConfigureAwait(false);
        var body = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
        if (!response.IsSuccessStatusCode)
            throw new HoroscoopApiException($"Horoscoop API error ({(int)response.StatusCode})", body);
        return JsonConvert.DeserializeObject(body);
    }

    public async Task<string> RenderWheelSvgAsync(
        string baseUrl,
        object body,
        CancellationToken cancellationToken = default)
    {
        var url = $"{baseUrl.TrimEnd('/')}/api/render/wheel.svg";
        var json = JsonConvert.SerializeObject(body);
        using var request = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = new StringContent(json, Encoding.UTF8, "application/json"),
        };
        using var response = await SharedClient.SendAsync(request, cancellationToken).ConfigureAwait(false);
        var content = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
        if (!response.IsSuccessStatusCode)
            throw new HoroscoopApiException("SVG render failed", content);
        return content;
    }

    public async Task<byte[]> RenderReportPdfAsync(
        string baseUrl,
        object body,
        CancellationToken cancellationToken = default)
    {
        var url = $"{baseUrl.TrimEnd('/')}/api/render/report.pdf";
        var json = JsonConvert.SerializeObject(body);
        using var request = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = new StringContent(json, Encoding.UTF8, "application/json"),
        };
        using var response = await SharedClient.SendAsync(request, cancellationToken).ConfigureAwait(false);
        var content = await response.Content.ReadAsByteArrayAsync().ConfigureAwait(false);
        if (!response.IsSuccessStatusCode)
            throw new HoroscoopApiException("PDF render failed", Encoding.UTF8.GetString(content));
        return content;
    }
}

public sealed class HoroscoopApiException : Exception
{
    public HoroscoopApiException(string message, string? responseBody = null)
        : base(message)
    {
        ResponseBody = responseBody;
    }

    public string? ResponseBody { get; }
}
