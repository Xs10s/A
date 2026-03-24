"""
Example CLI: compute horoscoop and print JSON.
Usage: python -m horoscoop.cli <date> [time] [lat] [lon]
      python -m horoscoop.cli 2000-01-01 12:00 52.0 5.0
"""
from __future__ import annotations

import argparse
import json
import sys


def main() -> None:
    ap = argparse.ArgumentParser(description="Horoscoop computation (reproducible astrology engine)")
    ap.add_argument("date", help="Birth date YYYY-MM-DD")
    ap.add_argument("time", nargs="?", default="12:00:00", help="Local time HH:MM:SS")
    ap.add_argument("lat", nargs="?", type=float, default=None, help="Latitude (deg)")
    ap.add_argument("lon", nargs="?", type=float, default=None, help="Longitude (deg)")
    ap.add_argument("--house-system", default="P", help="P,K,R,C,E,W,O,S")
    ap.add_argument("--ayanamsha", default="Lahiri", help="Sidereal mode")
    ap.add_argument("--utc-offset", type=float, default=None, help="UTC offset hours")
    ap.add_argument("--elevation", type=float, default=None, help="Elevation m")
    args = ap.parse_args()
    from .engine import compute
    out = compute(
        birth_date=args.date,
        birth_time_local=args.time,
        lat=args.lat,
        lon=args.lon,
        elevation_m=args.elevation,
        utc_offset_hours=args.utc_offset,
        house_system=args.house_system,
        ayanamsha_mode=args.ayanamsha,
    )
    json.dump(out, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
