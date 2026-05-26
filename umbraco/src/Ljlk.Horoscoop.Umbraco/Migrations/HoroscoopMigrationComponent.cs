using Umbraco.Cms.Core;
using Umbraco.Cms.Core.Composing;
using Umbraco.Cms.Core.Migrations;
using Umbraco.Cms.Core.Scoping;
using Umbraco.Cms.Core.Services;
using Umbraco.Cms.Infrastructure.Migrations;
using Umbraco.Cms.Infrastructure.Migrations.Upgrade;

namespace Ljlk.Horoscoop.Umbraco.Migrations;

public sealed class HoroscoopMigrationComponent : IComponent
{
    private readonly IMigrationPlanExecutor _executor;
    private readonly ICoreScopeProvider _scopeProvider;
    private readonly IKeyValueService _keyValueService;
    private readonly IRuntimeState _runtimeState;

    public HoroscoopMigrationComponent(
        IMigrationPlanExecutor executor,
        ICoreScopeProvider scopeProvider,
        IKeyValueService keyValueService,
        IRuntimeState runtimeState)
    {
        _executor = executor;
        _scopeProvider = scopeProvider;
        _keyValueService = keyValueService;
        _runtimeState = runtimeState;
    }

    public void Initialize()
    {
        if (_runtimeState.Level < RuntimeLevel.Run)
            return;

        var plan = new HoroscoopMigrationPlan();
        var upgrader = new Upgrader(plan);
        upgrader.Execute(_executor, _scopeProvider, _keyValueService);
    }

    public void Terminate()
    {
    }
}

public sealed class HoroscoopMigrationComposer : IComposer
{
    public void Compose(IUmbracoBuilder builder)
        => builder.Components().Append<HoroscoopMigrationComponent>();
}
