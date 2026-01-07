# routing/manoeuvre.py
from routing.stamina import StaminaModel


def apply_manoeuvre_with_stamina(
    bsp,
    manoeuvre_type,
    duration_sec,
    stamina_model,
    equipment_bonus=False
):
    """
    manoeuvre_type : 'tack', 'gybe', 'sail'
    equipment_bonus : True si Winch Pro ou Magic Furler
    """

    # consommation stamina
    stamina_model.consume(manoeuvre_type, wind=15)

    # facteur stamina
    stamina_factor = stamina_model.speed_factor()

    # pénalité de base
    penalty = 0.5  # -50%
    if equipment_bonus:
        penalty = 0.7  # -30%

    final_factor = penalty * stamina_factor
    bsp_after = bsp * final_factor

    return {
        "bsp_after": round(bsp_after, 2),
        "penalty_factor": round(final_factor, 3),
        "duration_sec": duration_sec,
        "stamina_left": round(stamina_model.stamina, 1),
    }
def detect_manoeuvre(prev_heading: float, new_heading: float) -> str | None:
    """
    Détecte si la variation de cap correspond à une manœuvre.
    - tack  (virement de bord) si on passe d'un bord à l'autre au près
    - gybe  (empannage) si on passe d'un bord à l'autre au portant
    """
    diff = (new_heading - prev_heading + 540) % 360 - 180

    # Tack ≈ changement brutal au près
    if abs(diff) > 30 and abs(prev_heading - 45) < 60:
        return "tack"

    # Gybe ≈ changement brutal au portant
    if abs(diff) > 30 and abs(prev_heading - 180) < 90:
        return "gybe"

    return None


from routing.stamina import StaminaModel


def apply_manoeuvre_with_stamina(
    bsp,
    manoeuvre_type,
    duration_sec=300,
    stamina_model: StaminaModel | None = None,
    equipment_bonus=False,
):
    """
    Applique une manoeuvre :
      - consomme de la stamina
      - applique une pénalité de vitesse pendant `duration_sec`
      - réduit la pénalité si équipement (Winch / Magic Furler)
    """

    # --- 1️⃣ Stamina (si modèle fourni) ---
    if stamina_model is not None:
        stamina_model.consume(manoeuvre_type, wind=15)
        stamina_factor = stamina_model.speed_factor()
    else:
        stamina_factor = 1.0

    # --- 2️⃣ Pénalité de manoeuvre ---
    penalty = 0.5          # -50% par défaut
    if equipment_bonus:
        penalty = 0.7      # -30% avec équipement

    final_factor = penalty * stamina_factor
    bsp_after = bsp * final_factor

    return {
        "bsp_after": round(bsp_after, 2),
        "penalty_factor": round(final_factor, 3),
        "duration_sec": duration_sec,
        "stamina_left": round(stamina_model.stamina, 1) if stamina_model else None,
    }

    return state

