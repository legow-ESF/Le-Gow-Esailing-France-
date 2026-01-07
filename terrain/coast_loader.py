import json
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "data" / "coast" / "raw"
CACHE_DIR = ROOT / "data" / "coast" / "cache"
CACHE_DIR.mkdir(exist_ok=True)

def load_geojson_coast(path):
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        geoms = []
        for feat in data.get("features", []):
            geom = feat.get("geometry")
            if not geom: continue
            if geom.get("type") == "GeometryCollection":
                for g in geom.get("geometries", []):
                    if g.get("type") in ("LineString", "Polygon"):
                        geoms.append(shape(g))
            elif geom.get("type") in ("LineString", "Polygon"):
                geoms.append(shape(geom))
        return geoms
    except:
        return []

def get_coast_in_bbox(min_lon, min_lat, max_lon, max_lat):
    geojson_files = list(CACHE_DIR.glob("dDalle_*.geojson"))
    if not geojson_files:
        from zipfile import ZipFile
        zips = list(RAW_DIR.glob("dDalle_*.zip"))
        for zip_path in zips:
            name = zip_path.stem
            cache_path = CACHE_DIR / f"{name}.geojson"
            if cache_path.exists(): continue
            try:
                with ZipFile(zip_path, 'r') as z:
                    for m in z.namelist():
                        if m.endswith(".geojson"):
                            with z.open(m) as src, open(cache_path, 'wb') as dst:
                                dst.write(src.read())
                            break
            except: pass
        geojson_files = list(CACHE_DIR.glob("dDalle_*.geojson"))

    all_geoms = []
    for path in geojson_files:
        all_geoms.extend(load_geojson_coast(path))

    return unary_union(all_geoms) if all_geoms else None