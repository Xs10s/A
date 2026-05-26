using Ljlk.Horoscoop.Umbraco.Models;
using Microsoft.AspNetCore.Mvc;
using Umbraco.Cms.Core.Security;
using Umbraco.Cms.Core.Web;

namespace Ljlk.Horoscoop.Umbraco.ViewComponents;

[ViewComponent(Name = "LjlkHoroscoopApp")]
public sealed class HoroscoopAppViewComponent : ViewComponent
{
    private readonly IUmbracoContextAccessor _umbracoContextAccessor;
    private readonly IMemberManager _memberManager;

    public HoroscoopAppViewComponent(
        IUmbracoContextAccessor umbracoContextAccessor,
        IMemberManager memberManager)
    {
        _umbracoContextAccessor = umbracoContextAccessor;
        _memberManager = memberManager;
    }

    public async Task<IViewComponentResult> InvokeAsync()
    {
        var loggedIn = false;
        if (_umbracoContextAccessor.TryGetUmbracoContext(out _))
        {
            var member = await _memberManager.GetCurrentMemberAsync().ConfigureAwait(false);
            loggedIn = member != null;
        }

        return View(new HoroscoopWidgetModel
        {
            LoggedIn = loggedIn,
            RestUrl = "/api/ljlk/v1/",
            StaticBase = "/ljlk-horoscoop/",
        });
    }
}
