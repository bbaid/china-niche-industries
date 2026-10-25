"""Convert data/clusters.csv into GIS-ready outputs.

Writes:
    data/clusters.geojson  - WGS84 points, opens directly in QGIS / ArcGIS / geojson.io
    web/index.html         - same GeoJSON embedded between /*DATA*/ ... /*END*/ so the
                             map is one self-contained file (no server needed)

Usage:
    python scripts/build.py
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "clusters.csv"
GEOJSON_PATH = ROOT / "data" / "clusters.geojson"
HTML_PATH = ROOT / "web" / "index.html"


def main():
    with CSV_PATH.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    features = []
    for row in rows:
        lat, lon = float(row.pop("lat")), float(row.pop("lon"))
        if not (18 <= lat <= 54 and 73 <= lon <= 135):
            raise ValueError(f"Row {row['id']} ({row['industry']}) is outside China: {lat}, {lon}")
        row["id"] = int(row["id"])
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},  # GeoJSON is lon, lat
            "properties": row,
        })

    collection = {"type": "FeatureCollection", "features": features}
    GEOJSON_PATH.write_text(json.dumps(collection, ensure_ascii=False, indent=1), encoding="utf-8")
    html = HTML_PATH.read_text(encoding="utf-8")
    data = json.dumps(collection, ensure_ascii=False).replace("</", "<\\/")
    html, n = re.subn(r"/\*DATA\*/.*?/\*END\*/", lambda _: f"/*DATA*/{data}/*END*/", html, flags=re.S)
    if n != 1:
        raise RuntimeError(f"Expected one /*DATA*/.../*END*/ block in {HTML_PATH}, found {n}")
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"{len(features)} clusters -> {GEOJSON_PATH.relative_to(ROOT)}, {HTML_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
