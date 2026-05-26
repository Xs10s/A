using Ljlk.Horoscoop.Core;
using Ljlk.Horoscoop.Umbraco.Services;
using Microsoft.Extensions.DependencyInjection;
using Umbraco.Cms.Core.Composing;
using Umbraco.Cms.Core.DependencyInjection;

namespace Ljlk.Horoscoop.Umbraco.Composer;

public sealed class HoroscoopComposer : IComposer
{
    public void Compose(IUmbracoBuilder builder)
    {
        builder.Services.AddSingleton<HoroscoopApiClient>();
        builder.Services.AddSingleton<RateLimiter>();
        builder.Services.Configure<HoroscoopSettings>(builder.Config.GetSection("LjlkHoroscoop"));
        builder.Services.AddScoped<IHoroscoopRepository, HoroscoopRepository>();
        builder.Services.AddScoped<IHoroscoopService, HoroscoopService>();
    }
}
