import os

BASE_POLAR_DIR = "data/polaires"


def get_polar_path(boat_class: str, option: str | None = None) -> str:
    """
    Construit le chemin vers une polaire valide.

    Exemples valides :
    - Imoca-nu.csv
    - Imoca-nu+foils.csv
    - Imoca-nu+code 0.csv
    """

    class_dir = os.path.join(BASE_POLAR_DIR, boat_class)

    if not os.path.isdir(class_dir):
        raise FileNotFoundError(f"Classe bateau inconnue : {boat_class}")

    if option is None or option == "nu":
        filename = f"{boat_class}-nu.csv"
    else:
        filename = f"{boat_class}-nu+{option}.csv"

    filepath = os.path.join(class_dir, filename)

    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Polaire introuvable : {filepath}")

    return filepath
