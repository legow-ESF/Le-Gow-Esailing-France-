import json
import os
import re

SRC = "Pénalités_files/bateau"
DST = "data/penalties"

os.makedirs(DST, exist_ok=True)

for file in os.listdir(SRC):
    if not file.endswith(".json"):
        continue

    path = os.path.join(SRC, file)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extraction du vrai JSON
    match = re.search(r"\{.*\}", content, re.S)
    if not match:
        print(f"❌ Impossible de parser {file}")
        continue

    json_text = match.group(0)

    try:
        data = json.loads(json_text)
    except Exception as e:
        print(f"❌ JSON invalide {file}: {e}")
        continue

    out_path = os.path.join(DST, file)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Converti : {file}")
