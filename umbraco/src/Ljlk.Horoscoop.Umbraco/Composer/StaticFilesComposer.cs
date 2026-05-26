using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.FileProviders;
using Umbraco.Cms.Core.Composing;
using Umbraco.Cms.Web.Common.ApplicationBuilder;

namespace Ljlk.Horoscoop.Umbraco.Composer;

public sealed class StaticFilesComposer : IComposer
{
    public void Compose(IUmbracoBuilder builder)
    {
        builder.Services.Configure<UmbracoPipelineOptions>(options =>
        {
            options.AddFilter(new UmbracoPipelineFilter("LjlkHoroscoopStatic")
            {
                PostPipeline = app =>
                {
                    var path = Path.Combine(AppContext.BaseDirectory, "wwwroot", "ljlk-horoscoop");
                    if (!Directory.Exists(path))
                        path = Path.Combine(AppContext.BaseDirectory, "ljlk-horoscoop");
                    if (!Directory.Exists(path))
                        return;

                    app.UseStaticFiles(new StaticFileOptions
                    {
                        FileProvider = new PhysicalFileProvider(path),
                        RequestPath = "/ljlk-horoscoop",
                    });
                },
            });
        });
    }
}
