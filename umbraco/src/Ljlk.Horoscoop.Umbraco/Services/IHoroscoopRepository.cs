using Ljlk.Horoscoop.Umbraco.Models;

namespace Ljlk.Horoscoop.Umbraco.Services;

public interface IHoroscoopRepository
{
    Task<int?> GetFirstProfileIdAsync(int memberId, CancellationToken cancellationToken = default);
    Task<int> CountProfilesAsync(int memberId, CancellationToken cancellationToken = default);
    Task<int> CreateProfileAsync(HoroscopeProfile profile, CancellationToken cancellationToken = default);
    Task<HoroscopeRun?> GetRunByHashAsync(int profileId, string inputHash, CancellationToken cancellationToken = default);
    Task<int> CountRunsForMemberAsync(int memberId, CancellationToken cancellationToken = default);
    Task<int> InsertRunAsync(HoroscopeRun run, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<HoroscopeProfile>> ListProfilesAsync(int memberId, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<HoroscopeRun>> ListRunsAsync(int profileId, CancellationToken cancellationToken = default);
    Task<HoroscopeRun?> GetRunForMemberAsync(int runId, int memberId, CancellationToken cancellationToken = default);
}
