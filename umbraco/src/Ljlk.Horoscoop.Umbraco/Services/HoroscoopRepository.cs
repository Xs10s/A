using Ljlk.Horoscoop.Umbraco.Models;
using NPoco;
using Umbraco.Cms.Infrastructure.Scoping;

namespace Ljlk.Horoscoop.Umbraco.Services;

public sealed class HoroscoopRepository : IHoroscoopRepository
{
    private readonly IScopeProvider _scopeProvider;

    public HoroscoopRepository(IScopeProvider scopeProvider)
    {
        _scopeProvider = scopeProvider;
    }

    public async Task<int?> GetFirstProfileIdAsync(int memberId, CancellationToken cancellationToken = default)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        var id = await scope.Database.ExecuteScalarAsync<int?>(
            "SELECT TOP 1 id FROM ljlkHoroscopeProfiles WHERE memberId = @0 ORDER BY id",
            memberId).ConfigureAwait(false);
        return id;
    }

    public async Task<int> CountProfilesAsync(int memberId, CancellationToken cancellationToken = default)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return await scope.Database.ExecuteScalarAsync<int>(
            "SELECT COUNT(*) FROM ljlkHoroscopeProfiles WHERE memberId = @0",
            memberId).ConfigureAwait(false);
    }

    public async Task<int> CreateProfileAsync(HoroscopeProfile profile, CancellationToken cancellationToken = default)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        var id = await scope.Database.InsertAsync("ljlkHoroscopeProfiles", "id", new
        {
            memberId = profile.MemberId,
            label = profile.Label,
            birthDate = profile.BirthDate,
            birthTime = profile.BirthTime,
            latitude = profile.Latitude,
            longitude = profile.Longitude,
            timezoneIana = profile.TimezoneIana,
            utcOffsetMinutes = profile.UtcOffsetMinutes,
            settingsJson = profile.SettingsJson,
            createdAt = profile.CreatedAt,
        }).ConfigureAwait(false);
        return Convert.ToInt32(id);
    }

    public async Task<HoroscopeRun?> GetRunByHashAsync(int profileId, string inputHash, CancellationToken cancellationToken = default)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return await scope.Database.FirstOrDefaultAsync<HoroscopeRun>(
            "SELECT id AS Id, profileId AS ProfileId, inputHash AS InputHash, engineVersion AS EngineVersion, computedAt AS ComputedAt, horoscoopJson AS HoroscoopJson, wheelSvg AS WheelSvg, reportPdf AS ReportPdf, reportPdfUrl AS ReportPdfUrl FROM ljlkHoroscopeRuns WHERE profileId = @0 AND inputHash = @1",
            profileId,
            inputHash).ConfigureAwait(false);
    }

    public async Task<int> CountRunsForMemberAsync(int memberId, CancellationToken cancellationToken = default)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return await scope.Database.ExecuteScalarAsync<int>(
            @"SELECT COUNT(*) FROM ljlkHoroscopeRuns r
              INNER JOIN ljlkHoroscopeProfiles p ON r.profileId = p.id
              WHERE p.memberId = @0",
            memberId).ConfigureAwait(false);
    }

    public async Task<int> InsertRunAsync(HoroscopeRun run, CancellationToken cancellationToken = default)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        var id = await scope.Database.InsertAsync("ljlkHoroscopeRuns", "id", new
        {
            profileId = run.ProfileId,
            inputHash = run.InputHash,
            engineVersion = run.EngineVersion,
            computedAt = run.ComputedAt,
            horoscoopJson = run.HoroscoopJson,
            wheelSvg = run.WheelSvg,
            reportPdf = run.ReportPdf,
            reportPdfUrl = run.ReportPdfUrl,
        }).ConfigureAwait(false);
        return Convert.ToInt32(id);
    }

    public async Task<IReadOnlyList<HoroscopeProfile>> ListProfilesAsync(int memberId, CancellationToken cancellationToken = default)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        var rows = await scope.Database.FetchAsync<HoroscopeProfile>(
            @"SELECT id AS Id, memberId AS MemberId, label AS Label, birthDate AS BirthDate,
                     birthTime AS BirthTime, latitude AS Latitude, longitude AS Longitude,
                     timezoneIana AS TimezoneIana, utcOffsetMinutes AS UtcOffsetMinutes,
                     settingsJson AS SettingsJson, createdAt AS CreatedAt
              FROM ljlkHoroscopeProfiles WHERE memberId = @0 ORDER BY id",
            memberId).ConfigureAwait(false);
        return rows;
    }

    public async Task<IReadOnlyList<HoroscopeRun>> ListRunsAsync(int profileId, CancellationToken cancellationToken = default)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        var rows = await scope.Database.FetchAsync<HoroscopeRun>(
            @"SELECT id AS Id, profileId AS ProfileId, inputHash AS InputHash, engineVersion AS EngineVersion,
                     computedAt AS ComputedAt, horoscoopJson AS HoroscoopJson, wheelSvg AS WheelSvg,
                     reportPdf AS ReportPdf, reportPdfUrl AS ReportPdfUrl
              FROM ljlkHoroscopeRuns WHERE profileId = @0 ORDER BY computedAt DESC",
            profileId).ConfigureAwait(false);
        return rows;
    }

    public async Task<HoroscopeRun?> GetRunForMemberAsync(int runId, int memberId, CancellationToken cancellationToken = default)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return await scope.Database.FirstOrDefaultAsync<HoroscopeRun>(
            @"SELECT r.id AS Id, r.profileId AS ProfileId, r.inputHash AS InputHash, r.engineVersion AS EngineVersion,
                     r.computedAt AS ComputedAt, r.horoscoopJson AS HoroscoopJson, r.wheelSvg AS WheelSvg,
                     r.reportPdf AS ReportPdf, r.reportPdfUrl AS ReportPdfUrl
              FROM ljlkHoroscopeRuns r
              INNER JOIN ljlkHoroscopeProfiles p ON r.profileId = p.id
              WHERE r.id = @0 AND p.memberId = @1",
            runId,
            memberId).ConfigureAwait(false);
    }
}
