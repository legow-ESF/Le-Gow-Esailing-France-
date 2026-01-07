# test_coast.py
import sys
import os
from pathlib import Path
import zipfile
import json
from shapely.geometry import Point, shape
from shapely.ops import unary_union

# --- CONFIG : ajuste si besoin ---
ROOT = Path(__file__).parent  # C:\Hugo\vr-routeur
DALLE_ZIP = ROOT / "data" / "coast" / "raw" / "dDalle_9_0_AB887AEC0275BE7BF3CD70F26D28B7B2.zip"
TEMP_DIR = ROOT / "data" / "coast" / "temp"

# --- 1. Extraire la dalle ---
print("🔍 Extraction de la dalle...")
TEMP_DIR.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(DALLE_ZIP, 'r') as z:
    z.extractall(TEMP_DIR)
print("✅ Dalle extraite dans", TEMP_DIR)

# --- 2. Trouver le .geojson ---
geojson_path = None
for p in TEMP_DIR.rglob("*.geojson"):
    geojson_path = p
    break

if not geojson_path:
    print("❌ Aucun .geojson trouvé dans le ZIP")
    sys.exit(1)

print("📄 Fichier GeoJSON trouvé :", geojson_path.name)

# --- 3. Charger les géométries ---
print("🌍 Chargement des géométries...")
with open(geojson_path, encoding='utf-8') as f:
    data = json.load(f)

geoms = []
for feat in data.get("features", []):
    geom = feat.get("geometry")
    if not geom:
        continue
    # Gère GeometryCollection (comme dans ton extrait)
    if geom.get("type") == "GeometryCollection":
        for g in geom.get("geometries", []):
            if g.get("type") in ("LineString", "Polygon", "MultiLineString"):
                geoms.append(shape(g))
    elif geom.get("type") in ("LineString", "Polygon", "MultiLineString"):
        geoms.append(shape(geom))

if not geoms:
    print("❌ Aucune géométrie valide trouvée")
    sys.exit(1)

# Fusionner → plus rapide pour les tests
coast_union = unary_union(geoms)
print(f"✅ {len(geoms)} géométries chargées → fusionnées en 1 objet")

# --- 4. Fonction is_land ---
def is_land(lat: float, lon: float, buffer_km: float = 0.1) -> bool:
    """
    Vérifie si (lat, lon) est sur terre ou très près.
    buffer_km : sécurité (ex. 100m = 0.1 km)
    """
    pt = Point(lon, lat)  # Shapely = (lon, lat) !
    # Buffer en degrés (~1 km ≈ 0.009° en moyenne)
    buffer_deg = buffer_km / 111.0
    return pt.within(coast_union.buffer(buffer_deg))

# --- 5. Tests ---
print("\n🧪 Tests :")

# Point sur la côte (d'après ton extrait : [9.0041096, -1.030137] etc.)
test_points = [
    ( -1.031, 9.004 ),   # lat, lon → doit être sur côte
    ( -1.040, 9.000 ),   # un peu plus au large → eau
    ( 48.45, -4.78 ),    # Ouessant (à tester plus tard)
]

for i, (lat, lon) in enumerate(test_points, 1):
    result = is_land(lat, lon, buffer_km=0.05)
    print(f"  Test {i}: ({lat:.5f}, {lon:.5f}) → {'🪨 TERRE' if result else '🌊 EAU'}")

print("\n🎉 Test terminé. Si le premier point est 'TERRE', tout fonctionne !")