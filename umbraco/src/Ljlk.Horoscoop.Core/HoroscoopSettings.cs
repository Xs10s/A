namespace Ljlk.Horoscoop.Core;

/// <summary>Runtime configuration for the horoscope integration.</summary>
public sealed class HoroscoopSettings
{
    public string ApiBaseUrl { get; set; } = string.Empty;
    public bool CacheSvgPdf { get; set; }
    public int MaxSavesPerUser { get; set; } = 10;
    public int RateLimitPerHour { get; set; } = 60;
}
