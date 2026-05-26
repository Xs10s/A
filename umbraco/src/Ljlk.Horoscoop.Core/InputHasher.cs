using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Ljlk.Horoscoop.Core;

public static class InputHasher
{
    private static readonly string[] CanonicalKeys =
    {
        "birth_date",
        "birth_time",
        "birth_time_local",
        "latitude",
        "longitude",
        "lat",
        "lon",
        "timezone_iana",
        "utc_offset_minutes",
        "utc_offset_hours",
        "settings",
    };

    public static string CanonicalJson(IDictionary<string, object?> payload)
    {
        var normalized = new SortedDictionary<string, object?>(StringComparer.Ordinal);
        foreach (var key in CanonicalKeys)
        {
            if (payload.TryGetValue(key, out var value))
                normalized[key] = NormalizeValue(key, value);
            else
                normalized[key] = null;
        }

        return JsonConvert.SerializeObject(
            normalized,
            Formatting.None,
            new JsonSerializerSettings
            {
                NullValueHandling = NullValueHandling.Include,
            });
    }

    public static string InputHash(IDictionary<string, object?> payload)
    {
        var json = CanonicalJson(payload);
        using var sha = SHA256.Create();
        var bytes = sha.ComputeHash(Encoding.UTF8.GetBytes(json));
        return BitConverter.ToString(bytes).Replace("-", string.Empty).ToLowerInvariant();
    }

    private static object? NormalizeValue(string key, object? value)
    {
        if (key == "settings" && value is JObject jobj)
        {
            var sorted = new SortedDictionary<string, JToken?>(StringComparer.Ordinal);
            foreach (var prop in jobj.Properties())
                sorted[prop.Name] = prop.Value;
            return sorted;
        }

        if (key == "settings" && value is IDictionary<string, object?> dict)
        {
            return new SortedDictionary<string, object?>(dict, StringComparer.Ordinal);
        }

        return value;
    }
}
