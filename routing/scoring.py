import math


def normalize_angle(a):
    return (a + 360) % 360


def angle_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def score_heading(
    heading,
    state,
    waypoint,
    tws,
    twd,
    bsp,
    manoeuvre_penalty=0.0,
):
    """
    Score d'un cap candidat
    Plus le score est GRAND, meilleur il est
    """

    # --- 1. Direction vers le waypoint
    bearing_wp = waypoint.bearing_from(state.lat, state.lon)
    diff_wp = angle_diff(heading, bearing_wp)

    # --- 2. VMG vers waypoint
    vmg = bsp * math.cos(math.radians(diff_wp))

    # --- 3. Bonus vent fort
    wind_bonus = tws * 0.3

    # --- 4. Bonus vent bien orienté (évite naviguer trop mal au vent)
    twa = angle_diff(heading, twd)
    orientation_bonus = max(0, 90 - abs(90 - twa)) * 0.1

    # --- 5. Distance finale (approximée)
    distance_penalty = diff_wp * 0.5

    # --- SCORE FINAL ---
    score = (
        vmg * 2.0
        + wind_bonus
        + orientation_bonus
        - manoeuvre_penalty
        - distance_penalty
    )

    return score
