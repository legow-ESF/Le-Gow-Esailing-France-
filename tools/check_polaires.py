import pandas as pd
import os
import itertools
import numpy as np

FOLDER = "data/polaires/Classe 40"
TOLERANCE = 0.3  # nds → acceptable pour polish / micro bonus

def load_polar(path):
    df = pd.read_csv(path)
    df = df.drop(columns=[df.columns[0]])  # enlève colonne TWA
    return df.values.astype(float)

files = [f for f in os.listdir(FOLDER) if f.endswith(".csv")]

polars = {}
for f in files:
    polars[f] = load_polar(os.path.join(FOLDER, f))

print("=== COMPARAISON DES POLAIRES ===\n")

for f1, f2 in itertools.combinations(files, 2):
    a = polars[f1]
    b = polars[f2]

    if a.shape != b.shape:
        print(f"❌ {f1} / {f2} → dimensions différentes")
        continue

    diff = np.abs(a - b)
    max_diff = diff.max()

    if max_diff == 0:
        print(f"🚨 IDENTIQUES : {f1} == {f2}")
    elif max_diff < TOLERANCE:
        print(f"⚠️ TRÈS PROCHES ({max_diff:.2f} nds) : {f1} ~ {f2}")
    else:
        print(f"✅ OK ({max_diff:.2f} nds) : {f1} / {f2}")
