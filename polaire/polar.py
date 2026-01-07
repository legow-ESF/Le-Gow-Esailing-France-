import os
import pandas as pd
import numpy as np


BASE_DIR = os.path.join("data", "polaires")


class Polar:
    def __init__(self, boat_class: str, option: str):
        """
        boat_class : exemple -> 'Imoca'
        option     : exemple -> 'nu', 'foils', 'code 0', 'légères', etc.

        Fichiers possibles (ex Imoca) :
            Imoca-nu.csv
            Imoca-nu+foils.csv
            Imoca-nu+code 0.csv
            Imoca-nu+lourdes.csv
            ...
        """

        # --- Normalisation des options ---
        if option is None or option.strip() == "":
            option = "nu"

        # Si l’option n'inclut pas déjà "nu", on la préfixe
        if not option.startswith("nu"):
            option = f"nu+{option}"

        # Construction du nom de fichier
        filename = f"{boat_class}-{option}.csv"
        filepath = os.path.join(BASE_DIR, boat_class, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Fichier polaire introuvable : {filepath}"
            )

        self.df = pd.read_csv(filepath)

        # TWA (lignes)
        self.twa_values = self.df.iloc[:, 0].astype(float).values

        # TWS (colonnes)
        self.tws_values = self.df.columns[1:].astype(float).values

        # BSP matrix
        self.bsp_matrix = self.df.iloc[:, 1:].astype(float).values

    def get_bsp(self, tws, twa):
        twa = abs(twa)

        twa = np.clip(twa, self.twa_values.min(), self.twa_values.max())
        tws = np.clip(tws, self.tws_values.min(), self.tws_values.max())

        bsp_twa = []
        for i in range(len(self.tws_values)):
            bsp = np.interp(twa, self.twa_values, self.bsp_matrix[:, i])
            bsp_twa.append(bsp)

        bsp_final = np.interp(tws, self.tws_values, bsp_twa)

        return float(bsp_final)

    def get_speed(self, tws, twa):
        return self.get_bsp(tws, twa)

    def best_twa(self, tws):
        best = {"twa": None, "bsp": 0.0}

        for twa in range(int(self.twa_values.min()),
                         int(self.twa_values.max()) + 1):
            bsp = self.get_bsp(tws, twa)
            if bsp > best["bsp"]:
                best["twa"] = twa
                best["bsp"] = bsp

        return best

    def best_vmg_upwind(self, tws):
        best = {"twa": None, "bsp": 0.0, "vmg": -1e9}

        for twa in range(30, 91):
            bsp = self.get_bsp(tws, twa)
            vmg = bsp * np.cos(np.radians(twa))

            if vmg > best["vmg"]:
                best["twa"] = twa
                best["bsp"] = bsp
                best["vmg"] = vmg

        return best

    def best_vmg_downwind(self, tws):
        best = {"twa": None, "bsp": 0.0, "vmg": -1e9}

        for twa in range(90, 151):
            bsp = self.get_bsp(tws, twa)
            vmg = bsp * np.cos(np.radians(180 - twa))

            if vmg > best["vmg"]:
                best["twa"] = twa
                best["bsp"] = bsp
                best["vmg"] = vmg

        return best
