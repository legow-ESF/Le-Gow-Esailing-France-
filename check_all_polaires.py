import os
import pandas as pd
import numpy as np
import hashlib

POLAR_FOLDER = "data/polaires"
TOL = 1e-6  # tolérance numérique (très stricte)

def normalize_df(df):
    """
    Normalise un DataFrame pour comparaison :
    - garde uniquement les valeurs numériques
    - remplace NaN
    - arrondit
    """
    df = df.copy()
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df.fillna(0.0)
    return np.round(df.values.astype(float), 6)

def hash_array(arr):
    """Crée une signature unique du contenu"""
    return hashlib.md5(arr.tobytes()).hexdigest()

polars = {}
duplicates = []

print("🔍 Analyse des polaires...\n")

for root, _, files in os.walk(POLAR_FOLDER):
    for f in files:
        if f.lower().endswith(".csv"):
            path = os.path.join(root, f)
            df = pd.read_csv(path)
            arr = normalize_df(df)
            h = hash_array(arr)

            if h in polars:
                duplicates.append((polars[h], path))
            else:
                polars[h] = path

# Résultats
if not duplicates:
    print("✅ AUCUN DOUBLON TROUVÉ")
else:
    print("❌ DOUBLONS DÉTECTÉS :\n")
    for a, b in duplicates:
        print(f"⚠️ {a}  ==  {b}")

print("\n✔ Analyse terminée")
