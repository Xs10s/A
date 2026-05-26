namespace Ljlk.Horoscoop.Umbraco.Models;

public sealed class HoroscopeRun
{
    public int Id { get; set; }
    public int ProfileId { get; set; }
    public string InputHash { get; set; } = string.Empty;
    public string? EngineVersion { get; set; }
    public DateTime ComputedAt { get; set; }
    public string HoroscoopJson { get; set; } = string.Empty;
    public string? WheelSvg { get; set; }
    public byte[]? ReportPdf { get; set; }
    public string? ReportPdfUrl { get; set; }
}
