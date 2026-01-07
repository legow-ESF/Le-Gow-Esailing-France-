import math
from dataclasses import dataclass

from polaire.polar import Polar
from routing.manoeuvre import detect_manoeuvre, apply_manoeuvre_with_stamina

DT_MIN = 10  # minutes


# ------------------ UTILITAIRES ------------------ #

def angle_diff(a, b):
    d = abs(a - b) % 360
    return d if d <= 180 else 360 - d


def bearing_to(lat1, lon1, lat2, lon2):
    dy = lat2 - lat1
    dx = lon2 - lon1
    return (math.degrees(math.atan2(dx, dy)) + 360) % 360


# ------------------ STRUCTURES ------------------ #

@dataclass
class BoatState:
    lat: float
    lon: float
    time_minutes: int
    stamina: float
    heading: float
    twa: float
    bsp: float
    boat_class: str
    option: str


@dataclass
class Waypoint:
    lat: float
    lon: float


# ------------------ LOGIQUE VMG ------------------ #

def choose_heading(state, wp, grib, polar):
    safe_time = min(state.time_minutes, grib.max_time_minutes - 1)
    tws, twd = grib.get_wind(state.lat, state.lon, safe_time)

    bearing = bearing_to(state.lat, state.lon, wp.lat, wp.lon)

    best = None

    for twa in range(30, 181):
        for sign in (-1, 1):
            real_twa = twa * sign
            heading = (twd + real_twa) % 360

            bsp = polar.get_speed(tws, abs(real_twa))
            if bsp is None:
                continue

            angle_to_wp = angle_diff(heading, bearing)
            vmg = bsp * math.cos(math.radians(angle_to_wp))

            if best is None or vmg > best[0]:
                best = (vmg, real_twa, heading, bsp)

    if best is None:
        return bearing, 0, 0, tws, twd

    _, twa, heading, bsp = best
    return heading, twa, bsp, tws, twd


# ------------------ AVANCEMENT ------------------ #

def advance_boat(state, wp, grib, polar, track):
    prev_twa = state.twa

    # Empêche de dépasser la dernière prévision du GRIB
    if hasattr(grib, "max_time_minutes") and state.time_minutes >= grib.max_time_minutes:
        return

    heading, twa, bsp, tws, twd = choose_heading(state, wp, grib, polar)

    manoeuvre = detect_manoeuvre(prev_twa, twa)

    if manoeuvre:
        result = apply_manoeuvre_with_stamina(
            bsp=bsp,
            manoeuvre_type=manoeuvre,
            duration_sec=DT_MIN * 60,
            stamina_model=None,
            equipment_bonus=False
        )
        bsp = result["bsp_after"]

    dist_nm = bsp * (DT_MIN / 60.0)
    dlat = dist_nm * math.cos(math.radians(heading)) / 60
    dlon = dist_nm * math.sin(math.radians(heading)) / 60

    state.lat += dlat
    state.lon += dlon
    state.time_minutes += DT_MIN
    state.heading = heading
    state.twa = twa
    state.bsp = bsp

    track.append((state.lat, state.lon))


# ------------------ BOUCLE PRINCIPALE ------------------ #

def run_route(state, waypoints, grib, polar, dt=DT_MIN, max_minutes=10080):
    track = [(state.lat, state.lon)]

    # GRIB : pas de 3 h → converti en minutes
    STEP_MINUTES = 180
    # essaie "step", sinon "time"
    step_dim = grib.ds.sizes.get("step", grib.ds.sizes.get("time"))
    grib.max_time_minutes = (step_dim - 1) * STEP_MINUTES
    print("GRIB MAX (min) =", grib.max_time_minutes)


    for wp in waypoints:
        while True:

            # 🛑 sécurité : fin météo ou durée max
            if state.time_minutes >= min(grib.max_time_minutes, max_minutes):
                print("STOP: météo terminée")
                break

            advance_boat(state, wp, grib, polar, track)

            # arrivée waypoint (proche)
            dist = math.hypot(wp.lat - state.lat, wp.lon - state.lon)
            if dist < 0.05:   # ≈ 3 NM suivant latitude
                break

    return state, track
