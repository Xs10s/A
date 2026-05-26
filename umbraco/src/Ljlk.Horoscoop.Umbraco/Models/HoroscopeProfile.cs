namespace Ljlk.Horoscoop.Umbraco.Models;

public sealed class HoroscopeProfile
{
    public int Id { get; set; }
    public int MemberId { get; set; }
    public string Label { get; set; } = "Mijn horoscoop";
    public DateTime BirthDate { get; set; }
    public TimeSpan? BirthTime { get; set; }
    public double? Latitude { get; set; }
    public double? Longitude { get; set; }
    public string? TimezoneIana { get; set; }
    public short? UtcOffsetMinutes { get; set; }
    public string? SettingsJson { get; set; }
    public DateTime CreatedAt { get; set; }
}
