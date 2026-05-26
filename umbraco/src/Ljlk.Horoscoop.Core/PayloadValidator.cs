using System;
using System.Globalization;
using System.Text.RegularExpressions;

namespace Ljlk.Horoscoop.Core;

public static class PayloadValidator
{
    private static readonly Regex TimeRegex = new Regex(
        @"^\d{1,2}:\d{2}(:\d{2})?$",
        RegexOptions.Compiled);

    public static bool ValidateBirthDate(string? date)
    {
        if (string.IsNullOrWhiteSpace(date) || date.Length < 10)
            return false;
        var slice = date.Substring(0, 10);
        return DateTime.TryParseExact(slice, "yyyy-MM-dd", CultureInfo.InvariantCulture, DateTimeStyles.None, out _);
    }

    public static bool ValidateBirthTime(string? time)
    {
        if (string.IsNullOrWhiteSpace(time))
            return true;
        return TimeRegex.IsMatch(time.Trim());
    }
}
