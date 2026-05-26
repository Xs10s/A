using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using NPoco;
using Umbraco.Core.Scoping;

namespace Ljlk.Horoscoop.Umbraco8.Services;

public sealed class HoroscoopRepository
{
    private readonly IScopeProvider _scopeProvider;

    public HoroscoopRepository(IScopeProvider scopeProvider)
    {
        _scopeProvider = scopeProvider;
    }

    public int? GetFirstProfileId(int memberId)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return scope.Database.ExecuteScalar<int?>(
            "SELECT TOP 1 id FROM ljlkHoroscopeProfiles WHERE memberId = @0 ORDER BY id",
            memberId);
    }

    public int CountProfiles(int memberId)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return scope.Database.ExecuteScalar<int>(
            "SELECT COUNT(*) FROM ljlkHoroscopeProfiles WHERE memberId = @0",
            memberId);
    }

    public int CreateProfile(object row)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return Convert.ToInt32(scope.Database.Insert("ljlkHoroscopeProfiles", "id", row));
    }

    public dynamic? GetRunByHash(int profileId, string inputHash)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return scope.Database.FirstOrDefault<dynamic>(
            "SELECT TOP 1 id, computedAt FROM ljlkHoroscopeRuns WHERE profileId = @0 AND inputHash = @1",
            profileId,
            inputHash);
    }

    public int CountRunsForMember(int memberId)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return scope.Database.ExecuteScalar<int>(
            @"SELECT COUNT(*) FROM ljlkHoroscopeRuns r
              INNER JOIN ljlkHoroscopeProfiles p ON r.profileId = p.id
              WHERE p.memberId = @0",
            memberId);
    }

    public int InsertRun(object row)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return Convert.ToInt32(scope.Database.Insert("ljlkHoroscopeRuns", "id", row));
    }

    public List<dynamic> ListProfiles(int memberId)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return scope.Database.Fetch<dynamic>(
            "SELECT id, label, birthDate, birthTime, createdAt FROM ljlkHoroscopeProfiles WHERE memberId = @0 ORDER BY id",
            memberId);
    }

    public List<dynamic> ListRuns(int profileId)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return scope.Database.Fetch<dynamic>(
            @"SELECT id, computedAt, wheelSvg, reportPdf, reportPdfUrl
              FROM ljlkHoroscopeRuns WHERE profileId = @0 ORDER BY computedAt DESC",
            profileId);
    }

    public dynamic? GetRunForMember(int runId, int memberId)
    {
        using var scope = _scopeProvider.CreateScope(autoComplete: true);
        return scope.Database.FirstOrDefault<dynamic>(
            @"SELECT r.*
              FROM ljlkHoroscopeRuns r
              INNER JOIN ljlkHoroscopeProfiles p ON r.profileId = p.id
              WHERE r.id = @0 AND p.memberId = @1",
            runId,
            memberId);
    }
}
