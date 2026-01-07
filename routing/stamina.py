# routing/stamina.py
import json
import os

STAMINA_FILE = "Pénalités_files/stamina.json"


class StaminaModel:
    def __init__(self, stamina=100):
        self.stamina = stamina
        self.rules = self.load_rules()

    def load_rules(self):
        if not os.path.exists(STAMINA_FILE):
            raise FileNotFoundError(f"Fichier stamina introuvable : {STAMINA_FILE}")
        with open(STAMINA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def recover(self, minutes, wind):
        """Récupération de stamina au repos"""
        recovery = self.rules["recovery"]

        lo = recovery["loTime"]
        hi = recovery["hiTime"]

        # interpolation simple
        rate = recovery["points"] / max(lo, min(hi, minutes))
        gained = rate * minutes

        self.stamina = min(100, self.stamina + gained)
        return self.stamina

    def consume(self, manoeuvre_type, wind):
        """Consommation de stamina"""
        base = self.rules["consumption"]["points"][manoeuvre_type]

        # facteur vent
        wind_factor = 1
        for w, f in self.rules["consumption"]["winds"].items():
            if wind >= int(w):
                wind_factor = f

        cost = base * wind_factor
        self.stamina = max(0, self.stamina - cost)
        return self.stamina

    def speed_factor(self):
        """Facteur de vitesse selon la stamina"""
        impact = self.rules["impact"]

        if self.stamina <= 0:
            return impact["0"]
        if self.stamina >= 100:
            return impact["100"]

        # interpolation linéaire
        return impact["100"] + (impact["0"] - impact["100"]) * (1 - self.stamina / 100)
