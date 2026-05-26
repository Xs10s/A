using Microsoft.AspNetCore.Http;

namespace Ljlk.Horoscoop.Umbraco.Services;

public interface IHoroscoopService
{
    Task<object> ComputeAsync(IReadOnlyDictionary<string, object?> body, string clientIp, CancellationToken cancellationToken = default);
    Task<object> SaveAsync(IReadOnlyDictionary<string, object?> body, int? memberId, CancellationToken cancellationToken = default);
    Task<object> ListMyAsync(int memberId, CancellationToken cancellationToken = default);
    Task<object?> DownloadJsonAsync(int runId, int memberId, CancellationToken cancellationToken = default);
    Task<(byte[] Content, string ContentType, string FileName)?> DownloadWheelAsync(int runId, int memberId, CancellationToken cancellationToken = default);
    Task<(byte[] Content, string ContentType, string FileName)?> DownloadReportAsync(int runId, int memberId, CancellationToken cancellationToken = default);
    Task<object> RegisterAsync(string email, string password, string clientIp, CancellationToken cancellationToken = default);
    Task<object> LoginAsync(string email, string password, HttpContext httpContext, CancellationToken cancellationToken = default);
}
