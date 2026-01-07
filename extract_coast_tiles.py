import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "data" / "coast" / "raw"
DST = BASE / "data" / "coast" / "geojson"

DST.mkdir(parents=True, exist_ok=True)

count = 0
for f in SRC.glob("*.KurunFile"):
    with zipfile.ZipFile(f, "r") as z:
        z.extractall(DST)
        count += 1

print(f"✅ Extraction terminée : {count} fichiers")
