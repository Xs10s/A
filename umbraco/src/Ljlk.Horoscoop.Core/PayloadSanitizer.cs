using System;
using System.Collections.Generic;

namespace Ljlk.Horoscoop.Core;

/// <summary>Maps CMS form fields to Python API payload keys.</summary>
public static class PayloadSanitizer
{
    public static Dictionary<string, object?> SanitizeForApi(IReadOnlyDictionary<string, object?> input)
    {
        var outPayload = new Dictionary<string, object?>(StringComparer.OrdinalIgnoreCase)
        {
            ["birth_date"] = GetString(input, "birth_date"),
            ["birth_time_local"] = null,
            ["lat"] = null,
            ["lon"] = null,
            ["timezone_iana"] = GetString(input, "timezone_iana"),
            ["utc_offset_minutes"] = SanitizeInt(input, "utc_offset_minutes", -720, 720),
        };

        var birthTime = GetString(input, "birth_time") ?? GetString(input, "birth_time_local");
        if (!string.IsNullOrWhiteSpace(birthTime))
            outPayload["birth_time_local"] = birthTime.Trim();

        if (TryGetDouble(input, "latitude", out var lat) || TryGetDouble(input, "lat", out lat))
            outPayload["lat"] = lat;
        if (TryGetDouble(input, "longitude", out var lon) || TryGetDouble(input, "lon", out lon))
            outPayload["lon"] = lon;

        if (input.TryGetValue("settings", out var settings) && settings is IDictionary<string, object?> settingsDict)
            outPayload["settings"] = settingsDict;

        return outPayload;
    }

    public static Dictionary<string, object?> ToHashPayload(
        IReadOnlyDictionary<string, object?> raw,
        Dictionary<string, object?> apiPayload)
    {
        var hash = new Dictionary<string, object?>(StringComparer.OrdinalIgnoreCase);
        foreach (var kv in raw)
            hash[kv.Key] = kv.Value;
        if (apiPayload.TryGetValue("birth_date", out var bd))
            hash["birth_date"] = bd;
        if (raw.TryGetValue("birth_time", out var bt))
            hash["birth_time"] = bt;
        return hash;
    }

    private static string? GetString(IReadOnlyDictionary<string, object?> input, string key)
    {
        if (!input.TryGetValue(key, out var value) || value == null)
            return null;
        var s = value.ToString()?.Trim();
        return string.IsNullOrEmpty(s) ? null : s;
    }

    private static int? SanitizeInt(IReadOnlyDictionary<string, object?> input, string key, int min, int max)
    {
        if (!input.TryGetValue(key, out var value) || value == null)
            return null;
        if (!int.TryParse(value.ToString(), out var n))
            return null;
        if (n < min || n > max)
            return null;
        return n;
    }

    private static bool TryGetDouble(IReadOnlyDictionary<string, object?> input, string key, out double result)
    {
        result = 0;
        if (!input.TryGetValue(key, out var value) || value == null)
            return false;
        if (value is double d)
        {
            result = d;
            return true;
        }
        return double.TryParse(
            value.ToString(),
            System.Globalization.NumberStyles.Float,
            System.Globalization.CultureInfo.InvariantCulture,
            out result);
    }
}
