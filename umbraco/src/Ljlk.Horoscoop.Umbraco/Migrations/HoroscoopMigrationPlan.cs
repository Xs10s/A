using Umbraco.Cms.Infrastructure.Migrations;

namespace Ljlk.Horoscoop.Umbraco.Migrations;

public sealed class HoroscoopMigrationPlan : MigrationPlan
{
    public HoroscoopMigrationPlan()
        : base("LjlkHoroscoop")
    {
        From(string.Empty).To<CreateHoroscopeTables>("ljlk-horoscoop-1");
    }
}
