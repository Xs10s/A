using System.Configuration;
using Ljlk.Horoscoop.Core;
using Ljlk.Horoscoop.Umbraco8.Services;
using Umbraco.Core;
using Umbraco.Core.Composing;
using Umbraco.Core.Migrations;
using Umbraco.Core.Migrations.Upgrade;
using Umbraco.Core.Scoping;
using Umbraco.Core.Services;
using Umbraco.Core.Logging;
using Umbraco.Core.Models.PublishedContent;

namespace Ljlk.Horoscoop.Umbraco8.Composer;

public sealed class HoroscoopComposer : IUserComposer
{
    public void Compose(Composition composition)
    {
        composition.Register<HoroscoopApiClient>();
        composition.Register<RateLimiter>();
        composition.Register<HoroscoopSettings>(factory =>
        {
            var section = ConfigurationManager.GetSection("ljlkHoroscoop") as System.Collections.Specialized.NameValueCollection;
            return new HoroscoopSettings
            {
                ApiBaseUrl = section?["apiBaseUrl"] ?? ConfigurationManager.AppSettings["LjlkHoroscoop:ApiBaseUrl"] ?? string.Empty,
                CacheSvgPdf = bool.TryParse(section?["cacheSvgPdf"] ?? ConfigurationManager.AppSettings["LjlkHoroscoop:CacheSvgPdf"], out var cache) && cache,
                MaxSavesPerUser = int.TryParse(section?["maxSavesPerUser"] ?? ConfigurationManager.AppSettings["LjlkHoroscoop:MaxSavesPerUser"], out var max) ? max : 10,
                RateLimitPerHour = int.TryParse(section?["rateLimitPerHour"] ?? ConfigurationManager.AppSettings["LjlkHoroscoop:RateLimitPerHour"], out var rate) ? rate : 60,
            };
        });
        composition.Register<HoroscoopRepository>();
        composition.Register<HoroscoopService>();
        composition.Components().Append<HoroscoopMigrationComponent>();
    }
}

public sealed class HoroscoopMigrationComponent : IComponent
{
    private readonly IScopeProvider _scopeProvider;
    private readonly IMigrationBuilder _migrationBuilder;
    private readonly IKeyValueService _keyValueService;
    private readonly IRuntimeState _runtimeState;
    private readonly ILogger _logger;

    public HoroscoopMigrationComponent(
        IScopeProvider scopeProvider,
        IMigrationBuilder migrationBuilder,
        IKeyValueService keyValueService,
        IRuntimeState runtimeState,
        ILogger logger)
    {
        _scopeProvider = scopeProvider;
        _migrationBuilder = migrationBuilder;
        _keyValueService = keyValueService;
        _runtimeState = runtimeState;
        _logger = logger;
    }

    public void Initialize()
    {
        if (_runtimeState.Level < RuntimeLevel.Run)
            return;

        var migration = new MigrationPlan("LjlkHoroscoop")
            .From(string.Empty)
            .To<CreateHoroscopeTablesMigration>("ljlk-horoscoop-1");

        var upgrader = new Upgrader(migration);
        upgrader.Execute(
            _scopeProvider,
            _migrationBuilder,
            _keyValueService,
            _logger);
    }

    public void Terminate()
    {
    }
}

public sealed class CreateHoroscopeTablesMigration : MigrationBase
{
    public CreateHoroscopeTablesMigration(IMigrationContext context)
        : base(context)
    {
    }

    public override void Migrate()
    {
        if (!TableExists("ljlkHoroscopeProfiles"))
        {
            Create.Table("ljlkHoroscopeProfiles")
                .WithColumn("id").AsInt32().Identity().PrimaryKey()
                .WithColumn("memberId").AsInt32().Indexed()
                .WithColumn("label").AsString(100).Nullable()
                .WithColumn("birthDate").AsDateTime()
                .WithColumn("birthTime").AsCustom("time").Nullable()
                .WithColumn("latitude").AsDouble().Nullable()
                .WithColumn("longitude").AsDouble().Nullable()
                .WithColumn("timezoneIana").AsString(64).Nullable()
                .WithColumn("utcOffsetMinutes").AsInt16().Nullable()
                .WithColumn("settingsJson").AsCustom("nvarchar(max)").Nullable()
                .WithColumn("createdAt").AsDateTime()
                .Do();
        }

        if (!TableExists("ljlkHoroscopeRuns"))
        {
            Create.Table("ljlkHoroscopeRuns")
                .WithColumn("id").AsInt32().Identity().PrimaryKey()
                .WithColumn("profileId").AsInt32().Indexed()
                .WithColumn("inputHash").AsString(64)
                .WithColumn("engineVersion").AsString(32).Nullable()
                .WithColumn("computedAt").AsDateTime()
                .WithColumn("horoscoopJson").AsCustom("nvarchar(max)")
                .WithColumn("wheelSvg").AsCustom("nvarchar(max)").Nullable()
                .WithColumn("reportPdf").AsCustom("varbinary(max)").Nullable()
                .WithColumn("reportPdfUrl").AsCustom("nvarchar(max)").Nullable()
                .Do();

            Create.Index("IX_ljlkHoroscopeRuns_profile_input")
                .OnTable("ljlkHoroscopeRuns")
                .OnColumn("profileId").Ascending()
                .OnColumn("inputHash").Ascending()
                .WithOptions()
                .Unique()
                .Do();
        }
    }
}
