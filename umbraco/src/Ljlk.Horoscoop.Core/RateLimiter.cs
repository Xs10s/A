using System;
using System.Collections.Concurrent;

namespace Ljlk.Horoscoop.Core;

/// <summary>In-memory sliding-window counter (per process). Suitable for single-instance sites.</summary>
public sealed class RateLimiter
{
    private readonly ConcurrentDictionary<string, Counter> _counters = new();

    public bool TryConsume(string key, int limit, TimeSpan window)
    {
        if (limit <= 0)
            return true;

        var now = DateTime.UtcNow;
        var counter = _counters.GetOrAdd(key, _ => new Counter());
        lock (counter)
        {
            if (counter.WindowStart == default || now - counter.WindowStart >= window)
            {
                counter.WindowStart = now;
                counter.Count = 0;
            }

            if (counter.Count >= limit)
                return false;

            counter.Count++;
            return true;
        }
    }

    private sealed class Counter
    {
        public DateTime WindowStart;
        public int Count;
    }
}
