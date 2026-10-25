# China's Niche Industry Towns — GIS map

A map of Chinese towns and counties that make a large share of a single product (buttons in Qiaotou, Christmas decorations in Yiwu, oil paintings in Dafen, and so on).

**Live map: https://bbaid.github.io/china-niche-industries/**. It redeploys automatically from `web/` on every push to `main`. Run `python scripts/build.py` before you commit, so the map includes your CSV changes.

```
data/clusters.csv        <- the source of truth; edit this
data/clusters.geojson    <- generated; load in QGIS / ArcGIS / geojson.io
scripts/build.py         <- CSV -> GeoJSON + embeds data into web/index.html
scripts/check_coords.py  <- checks every lat/lon against OpenStreetMap
web/index.html           <- interactive Leaflet map, data embedded by build.py (open directly in a browser)
```

## Workflow

1. Add or edit rows in `data/clusters.csv` (WGS84 decimal degrees; `search_zh` is a Baidu search phrase used for checking).
2. `python scripts/check_coords.py` geocodes each `place_zh, city_zh` with Nominatim and flags rows more than 15 km off. Read the flagged rows rather than accepting them blindly. The geocoder often picks a business with the city's name, or the middle of a county's land area instead of the town itself.
3. `python scripts/build.py`
4. Open `web/index.html`, or load `data/clusters.geojson` in QGIS.

### Data caveats

- **Market-share claims are "reported" figures.** Most come from press coverage in the 2000s–2010s, get repeated without a primary source, and some are out of date: Dafen shrank after 2008, and lighter making largely moved from Wenzhou to Shaodong. Before you publish a claim, trace it to an industry-association or government source.
- **Points mark the town or city centre**, accurate to about 1–10 km. They don't show where the factories are.
- 54 of the 61 points are within 15 km of OpenStreetMap's location. For the other 7, the geocoder matched the wrong thing (a company with the city's name, a different place called Shuibei, a county's centroid), so those were checked by hand.

---

## Sources for finding more clusters

### 1. Official "capital of X" designations (best starting point)
Chinese industry bodies give out titles like **中国X之乡** ("China's home of X"), **中国X之都** ("capital of X") and **中国X名城** ("famous city of X"). Searching those patterns, e.g. `"中国纽扣之都"` or `"之乡" 轻工业`, turns up most clusters.

| Source | What it gives you | Search for |
|---|---|---|
| **China Light Industry Council** (中国轻工业联合会) | "Light-industry characteristic regions & clusters" — pens, pianos, toys, lighters, knives… | `中国轻工业特色区域和产业集群 名单` |
| **China National Textile & Apparel Council** (中国纺织工业联合会, CNTAC) | ~200 textile cluster towns (socks, ties, jeans, swimwear, underwear) | `纺织产业集群试点 名单` |
| **MIIT SME Characteristic Industrial Clusters** (工信部 中小企业特色产业集群) | Annual national lists since 2022, ~100 per batch, county-level, with the product named | `中小企业特色产业集群 名单 工业和信息化部` |
| **Ministry of Agriculture "One Village One Product"** (全国一村一品示范村镇) | Village-level lists, each with its single product; also 农业产业强镇 | `一村一品示范村镇 名单` |
| **CNIPA Geographical Indications** (地理标志产品) | Craft and agricultural products tied to a named place | CNIPA GI database |
| **Provincial programmes** | Guangdong 专业镇 ("specialised towns", ~400); Zhejiang 块状经济 / 特色小镇 | `广东省 专业镇 名单`, `浙江 块状经济` |

### 2. E-commerce and firm-registry data (for density, not just points)
- **Taobao Villages** (淘宝村), annual AliResearch report: thousands of villages where online sellers cluster, often around a single product (Cao County Hanfu, Shaji furniture).
- **1688.com** (Alibaba wholesale): search a product, then look at the supplier-location filter. A quick way to discover which city dominates.
- **Qichacha / Tianyancha / Aiqicha** (企查查 / 天眼查 / 爱企查): count registered firms by business-scope keyword by county. Good for a heatmap or choropleth. Bulk exports need a paid plan.
- **China Industrial Enterprise Database** (中国工业企业数据库, 1998–2013): firm-level, with addresses and main product. Usually available through a university licence.
- **Customs statistics by domestic origin** (海关统计 境内货源地): exports by province or city per HS code.

### 3. Research and journalism
- **Wang Jici** (王缉慈), *创新的空间: 产业集群与区域发展*: the standard Chinese-language work on industrial clusters.
- **Xiaobo Zhang** (IFPRI / Peking University) and co-authors' papers on "cluster-based industrialization" (e.g. the Puyuan sweater cluster).
- Features in Sixth Tone, Rest of World, SCMP, Caixin; Chinese 县域经济 ("county economy") reporting in 第一财经 and 36Kr.
- Searching Google Scholar for "China specialized town industrial cluster" (or CNKI for `专业镇 产业集群`) turns up case studies.

### 4. GIS base data
| Data | Source | Notes |
|---|---|---|
| County (ADM3) boundaries | **geoBoundaries** `CHN ADM3`, **GADM 4.1** level 3 | WGS84, free |
| Up-to-date admin boundaries with adcodes | **DataV.GeoAtlas** (datav.aliyun.com) | Reportedly GCJ-02, so check alignment against OSM before joining |
| Township boundaries | OpenStreetMap `admin_level=8` (via Overpass/QuickOSM) | Coverage is patchy |
| Basemaps | OSM, Esri Gray Canvas, **Tianditu** 天地图 (free key, CGCS2000 ≈ WGS84) | |
| Geocoding | Nominatim (used here), Amap API | Amap returns GCJ-02 |

> **China coordinate gotcha:** coordinates copied from Amap/Gaode or Tencent are in **GCJ-02**, and Baidu's are **BD-09**. Both sit roughly 300–600 m off OSM/WGS84. Convert them first, e.g. with the Python `eviltransform` package or the GeoHey Toolbox plugin in QGIS.

---

## QGIS recipe

1. **Load points:** *Layer → Add Layer → Add Vector Layer →* `data/clusters.geojson` (EPSG:4326).
2. **Basemap:** *Browser → XYZ Tiles → OpenStreetMap*. For a quieter background, add a new XYZ connection: `https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}` (Esri Light Gray, no key needed).
3. **Style:** *Layer Properties → Symbology → Categorized*, value `category`, *Classify*.
4. **Labels:** *Labels → Single labels*, value `industry` or `industry || '\n' || place_zh`. Use a CJK-capable font such as Microsoft YaHei or Noto Sans CJK, or the Chinese renders as boxes.
5. **Projection for a nicer national map:** *Project → Properties → CRS →* `ESRI:102025` (Asia North Albers Equal Area Conic).
6. **County choropleth** (once you have more data): load geoBoundaries ADM3, then *Vector → Data Management Tools → Join Attributes by Location (Summary)* with the points and a `count` summary, and style the result *Graduated*.
7. **Export:** *Project → New Print Layout*, add the map, legend and scale bar, then export PNG or PDF.

Python alternative (`pip install geopandas matplotlib contextily`):

```python
import geopandas as gpd, contextily as cx
g = gpd.read_file("data/clusters.geojson").to_crs(3857)
ax = g.plot(column="category", legend=True, markersize=40, figsize=(12, 10))
cx.add_basemap(ax, source=cx.providers.Esri.WorldGrayCanvas)
ax.figure.savefig("china_clusters.png", dpi=200, bbox_inches="tight")
```

## Candidates to add next
Nankang 南康 (furniture), Shuyang 沭阳 (flowers & nursery plants), Nanxun 南浔 (wood flooring), Shishi 石狮 (casual wear), Houjie 厚街, Dongguan (shoes), Chaozhou 潮州 (ceramics & sanitary ware).
