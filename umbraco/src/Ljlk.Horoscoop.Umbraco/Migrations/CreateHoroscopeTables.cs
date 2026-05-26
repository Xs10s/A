using Microsoft.Extensions.Logging;
using NPoco;
using Umbraco.Cms.Infrastructure.Migrations;
using Umbraco.Cms.Infrastructure.Persistence.DatabaseAnnotations;

namespace Ljlk.Horoscoop.Umbraco.Migrations;

public sealed class CreateHoroscopeTables : MigrationBase
{
    public CreateHoroscopeTables(IMigrationContext context)
        : base(context)
    {
    }

    protected override void Migrate()
    {
        if (!TableExists("ljlkHoroscopeProfiles"))
            Create.Table<HoroscopeProfileSchema>().Do();

        if (!TableExists("ljlkHoroscopeRuns"))
        {
            Create.Table<HoroscopeRunSchema>().Do();
            if (!IndexExists("IX_ljlkHoroscopeRuns_profile_input"))
            {
                Create.Index("IX_ljlkHoroscopeRuns_profile_input")
                    .OnTable("ljlkHoroscopeRuns")
                    .OnColumn("profileId").Ascending()
                    .OnColumn("inputHash").Ascending()
                    .WithOptions().Unique()
                    .Do();
            }
        }

        Logger.LogInformation("LJLK Horoscoop tables ensured.");
    }

    [TableName("ljlkHoroscopeProfiles")]
    [PrimaryKey("id", AutoIncrement = true)]
    [ExplicitColumns]
    private sealed class HoroscopeProfileSchema
    {
        public int Id { get; set; }
        public int MemberId { get; set; }

        [Length(100)]
        [NullSetting(NullSetting = NullSettings.Null)]
        public string? Label { get; set; }

        public DateTime BirthDate { get; set; }

        [NullSetting(NullSetting = NullSettings.Null)]
        public TimeSpan? BirthTime { get; set; }

        [NullSetting(NullSetting = NullSettings.Null)]
        public double? Latitude { get; set; }

        [NullSetting(NullSetting = NullSettings.Null)]
        public double? Longitude { get; set; }

        [Length(64)]
        [NullSetting(NullSetting = NullSettings.Null)]
        public string? TimezoneIana { get; set; }

        [NullSetting(NullSetting = NullSettings.Null)]
        public short? UtcOffsetMinutes { get; set; }

        [SpecialDbType(SpecialDbTypes.NVARCHARMAX)]
        [NullSetting(NullSetting = NullSettings.Null)]
        public string? SettingsJson { get; set; }

        public DateTime CreatedAt { get; set; }
    }

    [TableName("ljlkHoroscopeRuns")]
    [PrimaryKey("id", AutoIncrement = true)]
    [ExplicitColumns]
    private sealed class HoroscopeRunSchema
    {
        public int Id { get; set; }
        public int ProfileId { get; set; }

        [Length(64)]
        public string InputHash { get; set; } = string.Empty;

        [Length(32)]
        [NullSetting(NullSetting = NullSettings.Null)]
        public string? EngineVersion { get; set; }

        public DateTime ComputedAt { get; set; }

        [SpecialDbType(SpecialDbTypes.NVARCHARMAX)]
        public string HoroscoopJson { get; set; } = string.Empty;

        [SpecialDbType(SpecialDbTypes.NVARCHARMAX)]
        [NullSetting(NullSetting = NullSettings.Null)]
        public string? WheelSvg { get; set; }

        [SpecialDbType(SpecialDbTypes.NVARCHARMAX)]
        [NullSetting(NullSetting = NullSettings.Null)]
        public byte[]? ReportPdf { get; set; }

        [SpecialDbType(SpecialDbTypes.NVARCHARMAX)]
        [NullSetting(NullSetting = NullSettings.Null)]
        public string? ReportPdfUrl { get; set; }
    }
}
