"""Check each cluster's coordinates against OpenStreetMap Nominatim.

Looks up "<place_zh>, <city_zh>" and reports how far the geocoded point is from
the lat/lon in clusters.csv. Rows further than --max-km away are flagged so you
can fix them by hand. Respects Nominatim's 1 request/second policy.

Usage:
    python scripts/check_coords.py              # report only
    python scripts/check_coords.py --write      # also write data/geocoded.csv
"""

import argparse
import csv
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "clusters.csv"
OUT_PATH = ROOT / "data" / "geocoded.csv"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "china-niche-industry-map/0.1 (personal research project)"


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def geocode(query):
    params = urllib.parse.urlencode(
        {"q": query, "format": "jsonv2", "countrycodes": "cn", "limit": 1}
    )
    req = urllib.request.Request(f"{NOMINATIM}?{params}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        results = json.load(resp)
    if not results:
        return None
    hit = results[0]
    return float(hit["lat"]), float(hit["lon"]), hit.get("display_name", "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-km", type=float, default=15.0)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252

    with CSV_PATH.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = []
    for row in rows:
        query = f"{row['place_zh']}, {row['city_zh']}"
        try:
            hit = geocode(query)
        except Exception as exc:  # network errors shouldn't kill the whole run
            hit = None
            print(f"[{row['id']:>2}] ERROR {query}: {exc}")
        time.sleep(1.1)

        if hit is None:
            status, dist, g_lat, g_lon, name = "NOT FOUND", None, "", "", ""
        else:
            g_lat, g_lon, name = hit
            dist = haversine_km(float(row["lat"]), float(row["lon"]), g_lat, g_lon)
            status = "OK" if dist <= args.max_km else "CHECK"
        dist_s = f"{dist:6.1f} km" if dist is not None else "     -   "
        print(f"[{row['id']:>2}] {status:9} {dist_s}  {row['industry']} - {query}")
        results.append({**row, "geo_lat": g_lat, "geo_lon": g_lon,
                        "geo_km": "" if dist is None else round(dist, 1),
                        "geo_status": status, "geo_name": name})

    if args.write:
        with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
        print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
