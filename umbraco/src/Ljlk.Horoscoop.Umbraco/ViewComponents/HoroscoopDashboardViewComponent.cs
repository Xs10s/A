using Ljlk.Horoscoop.Umbraco.Models;
using Microsoft.AspNetCore.Mvc;
using Umbraco.Cms.Core.Security;

namespace Ljlk.Horoscoop.Umbraco.ViewComponents;

[ViewComponent(Name = "LjlkHoroscoopDashboard")]
public sealed class HoroscoopDashboardViewComponent : ViewComponent
{
    private readonly IMemberManager _memberManager;

    public HoroscoopDashboardViewComponent(IMemberManager memberManager)
    {
        _memberManager = memberManager;
    }

    public async Task<IViewComponentResult> InvokeAsync()
    {
        var member = await _memberManager.GetCurrentMemberAsync().ConfigureAwait(false);
        return View(new HoroscoopWidgetModel
        {
            LoggedIn = member != null,
            RestUrl = "/api/ljlk/v1/",
            StaticBase = "/ljlk-horoscoop/",
        });
    }
}
