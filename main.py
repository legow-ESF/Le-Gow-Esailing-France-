from meteo.grib import GribFile
from routing.engine import BoatState, Waypoint, run_route
import json

GRIB_PATH = "data/meteo/gfs.grib2"

state = BoatState(
    lat=0.0,
    lon=0.0,
    time_minutes=0,
    stamina=100.0,
    heading=90.0,
    twa=130.0,
    bsp=0.0,
    boat_class="Imoca",
    option="nu"
)

waypoint = Waypoint(
    lat=5.0,
    lon=5.0
)

grib = GribFile(GRIB_PATH)

final_state, track = run_route(
    state=state,
    waypoint=waypoint,
    grib=grib,
    duration_minutes=300
)

print("\n--- FIN ---")
print(f"Position finale : {final_state.lat:.4f}, {final_state.lon:.4f}")

with open("track.json", "w") as f:
    json.dump(track, f)

print("Track sauvegardé -> track.json")
