# terrain/tile_generator.py
import math
import json
from pathlib import Path
from shapely.geometry import shape, box
from shapely.ops import unary_union

ROOT = Path(__file__).parent.parent
CACHE_DIR = ROOT / "data" / "coast" / "cache"
TILES_DIR = ROOT / "data" / "coast" / "tiles"
TILES_DIR.mkdir(parents=True, exist_ok=True)

def load_all_geoms():
    geoms = []
    for path in CACHE_DIR.glob("dDalle_*.geojson"):
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        for feat in data.get("features", []):
            geom = feat.get("geometry")
            if geom and geom.get("type") in ("LineString", "Polygon"):
                geoms.append(shape(geom))
    return unary_union(geoms)

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return xtile, ytile

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg

def tile_bbox(z, x, y):
    n = 2.0 ** z
    min_lon = x / n * 360.0 - 180.0
    max_lon = (x + 1) / n * 360.0 - 180.0
    lat_rad1 = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_rad2 = math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))
    min_lat = math.degrees(lat_rad2)
    max_lat = math.degrees(lat_rad1)
    return min_lon, min_lat, max_lon, max_lat

def generate_tiles():
    print("🌍 Chargement de toutes les géométries...")
    coast_geom = load_all_geoms()
    print("✅ Géométries chargées. Génération des tuiles...")

    # Zooms utiles : 4 (mondial) → 12 (détail)
    for z in range(4, 13):
        print(f"  → Zoom {z}...")
        (TILES_DIR / f"z{z}").mkdir(exist_ok=True)
        # Parcourt toutes les tuiles couvrant [-180,180] × [-85,85]
        max_tile = 2 ** z
        for x in range(0, max_tile):
            for y in range(0, max_tile):
                # Bbox de la tuile
                min_lon, min_lat, max_lon, max_lat = tile_bbox(z, x, y)
                # Si trop près des pôles, skip
                if abs(min_lat) > 85 or abs(max_lat) > 85:
                    continue

                # Coupe la géométrie dans la tuile
                tile_box = box(min_lon, min_lat, max_lon, max_lat)
                clipped = coast_geom.intersection(tile_box)
                if clipped.is_empty:
                    continue

                # Convertir en GeoJSON
                features = []
                geoms = [clipped] if clipped.geom_type in ("LineString", "Polygon") else list(clipped.geoms)
                for g in geoms:
                    if g.geom_type in ("LineString", "Polygon"):
                        features.append({
                            "type": "Feature",
                            "properties": {},
                            "geometry": {"type": g.geom_type, "coordinates": list(g.coords) if g.geom_type == "LineString" else list(g.exterior.coords)}
                        })

                if features:
                    tile_path = TILES_DIR / f"z{z}" / f"x{x}"
                    tile_path.mkdir(exist_ok=True)
                    with open(tile_path / f"y{y}.geojson", 'w', encoding='utf-8') as f:
                        json.dump({"type": "FeatureCollection", "features": features}, f, separators=(',', ':'))

    print("✅ Tuiles générées dans", TILES_DIR)

if __name__ == "__main__":
    generate_tiles()