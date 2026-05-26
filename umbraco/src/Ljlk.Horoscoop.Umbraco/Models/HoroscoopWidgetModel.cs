namespace Ljlk.Horoscoop.Umbraco.Models;

public sealed class HoroscoopWidgetModel
{
    public bool LoggedIn { get; set; }
    public string RestUrl { get; set; } = "/api/ljlk/v1/";
    public string StaticBase { get; set; } = "/ljlk-horoscoop/";
}
