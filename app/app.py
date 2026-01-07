import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify, render_template

print(">>> APP STARTING")

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

GRIB_PATH = ROOT_DIR / "data" / "meteo" / "gfs.grb2"
print("GRIB PATH =", GRIB_PATH)
print("Exists ?", GRIB_PATH.exists())

# ----- imports du routeur -----
from routing.engine import run_route, BoatState, Waypoint
from polaire.polar import Polar
from meteo.grib import GribFile

GRIB = GribFile(str(GRIB_PATH)) if GRIB_PATH.exists() else None
if GRIB is None:
    print("❌ GRIB non trouvé !")

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/route")
def api_route():
    try:
        lat0 = float(request.args.get("lat", 0))
        lon0 = float(request.args.get("lon", 0))
        lat1 = float(request.args.get("lat2", 10))
        lon1 = float(request.args.get("lon2", 10))
        boat_class = request.args.get("boat", "Imoca")
        option = request.args.get("option", "nu")

        polar = Polar(boat_class, option)
        state = BoatState(lat=lat0, lon=lon0, time_minutes=0, stamina=100, heading=0, twa=0, bsp=0, boat_class=boat_class, option=option)
        wp = Waypoint(lat1, lon1)

        if GRIB is None:
            return jsonify({"error": "GRIB missing"}), 500

        STEP_MINUTES = 180
        grib_minutes = (GRIB.ds.sizes.get("step", 1) - 1) * STEP_MINUTES
        duration_minutes = min(10 * 24 * 60, grib_minutes)

        final_state, track = run_route(state, [wp], GRIB, polar, max_minutes=duration_minutes)
        return jsonify({"track": track})

    except Exception as e:
        print("❌ Erreur /api/route:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(">>> Flask running on http://localhost:5000")
    app.run(debug=False, host="127.0.0.1", port=5000)