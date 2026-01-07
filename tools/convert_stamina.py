import json
import re
from pathlib import Path

INPUT_FILE = "Pénalités_files/stamina.json"
OUTPUT_FILE = "data/stamina.json"

def convert_stamina():
    raw = Path(INPUT_FILE).read_text(encoding="utf-8").strip()

    # Supprime "stamina1 =" ou tout ce qui est avant le premier {
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("❌ Impossible de trouver un objet JSON dans le fichier")

    json_text = match.group(0)

    # Vérification JSON
    data = json.loads(json_text)

    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FILE).write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

    print("✅ stamina.json converti avec succès →", OUTPUT_FILE)


if __name__ == "__main__":
    convert_stamina()
