import math
import xarray as xr
import numpy as np
import warnings

# --- SUPPRIMER LE WARNING xarray "dims" ---
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=".*Dataset.dims.*"
)



# =========================
# CONVERSION U/V → TWS/TWD
# =========================

def uv_to_tws_twd(u, v):
    tws = (u**2 + v**2) ** 0.5 * 1.94384
    twd = (270 - math.degrees(math.atan2(v, u))) % 360
    return tws, twd


# =========================
# LECTEUR GRIB
# =========================

class GribFile:
    def __init__(self, path):
        self.ds = xr.open_dataset(path)

    def get_wind(self, lat, lon, time_minutes: int):
        """
        Retourne (tws, twd) pour une position et un instant donné.
        time_minutes = minutes depuis le départ.
        Gère automatiquement les GRIB en pas 1h, 3h, etc.
        """

        ds = self.ds

        # ---- durée réelle d’un pas météo (ex: 60 min, 180 min, etc.) ----
        if "step" in ds.dims:
            try:
                step_minutes = int(
                    (ds["step"][1] - ds["step"][0])
                    .astype("timedelta64[m]")
                    / np.timedelta64(1, "m")
                )
            except Exception:
                step_minutes = 60
        else:
            step_minutes = 60

        # index du pas météo correspondant
        step_index = int(time_minutes // step_minutes)

        # sécurité si on dépasse le GRIB
        max_steps = ds.dims.get("step", step_index + 1)
        step_index = min(step_index, max_steps - 1)

        # ---- lecture vent ----
        if "time" in ds.dims:
            u = float(
                ds["u10"]
                .isel(time=step_index)
                .sel(latitude=lat, longitude=lon, method="nearest")
            )
            v = float(
                ds["v10"]
                .isel(time=step_index)
                .sel(latitude=lat, longitude=lon, method="nearest")
            )

        elif "step" in ds.dims:
            u = float(
                ds["u10"]
                .isel(step=step_index)
                .sel(latitude=lat, longitude=lon, method="nearest")
            )
            v = float(
                ds["v10"]
                .isel(step=step_index)
                .sel(latitude=lat, longitude=lon, method="nearest")
            )

        else:
            raise ValueError("GRIB inconnu : ni 'time' ni 'step' trouvés.")

        tws = math.sqrt(u * u + v * v)
        twd = (270 - math.degrees(math.atan2(v, u))) % 360
        return tws, twd


# =========================
# VENT INTERPOLÉ (PRO)
# =========================

def wind_at_position(ds, lat, lon, step_index=0):

    # GFS : 0–360
    if lon < 0:
        lon += 360

    ds_step = ds.isel(step=step_index)

    try:
        u = ds_step["u10"].interp(latitude=lat, longitude=lon, method="linear")
        v = ds_step["v10"].interp(latitude=lat, longitude=lon, method="linear")

        u = float(u.values)
        v = float(v.values)

        if math.isnan(u) or math.isnan(v):
            raise ValueError("NaN after linear interp")

    except Exception:
        u = float(
            ds_step["u10"]
            .sel(latitude=lat, longitude=lon, method="nearest")
            .values
        )
        v = float(
            ds_step["v10"]
            .sel(latitude=lat, longitude=lon, method="nearest")
            .values
        )

    tws, twd = uv_to_tws_twd(u, v)

    return {
        "u": round(u, 3),
        "v": round(v, 3),
        "tws": round(tws, 2),
        "twd": round(twd, 1),
    }


from datetime import timedelta


def wind_along_route(ds, route, step_start=0, step_minutes=10):
    results = []
    step_index = step_start

    for i, (lat, lon) in enumerate(route):
        wind = wind_at_position(ds, lat, lon, step_index)

        results.append({
            "index": i,
            "lat": lat,
            "lon": lon,
            "u": wind["u"],
            "v": wind["v"],
            "tws": wind["tws"],
            "twd": wind["twd"],
        })

        if (i + 1) * step_minutes >= 60:
            step_index += 1

    return results


def interpolate_uv_time(u0, v0, u1, v1, alpha):
    u = u0 + alpha * (u1 - u0)
    v = v0 + alpha * (v1 - v0)
    return u, v


def wind_at_position_time(ds, lat, lon, step0, step1, alpha):
    p0 = ds.isel(step=step0).interp(latitude=lat, longitude=lon)
    p1 = ds.isel(step=step1).interp(latitude=lat, longitude=lon)

    u0 = float(p0["u10"])
    v0 = float(p0["v10"])
    u1 = float(p1["u10"])
    v1 = float(p1["v10"])

    u, v = interpolate_uv_time(u0, v0, u1, v1, alpha)
    tws, twd = uv_to_tws_twd(u, v)

    return {"u": round(u, 3), "v": round(v, 3), "tws": round(tws, 2), "twd": round(twd, 1)}


def interpolate_uv(u0, v0, u1, v1, alpha):
    u = u0 + alpha * (u1 - u0)
    v = v0 + alpha * (v1 - v0)
    return u, v


def wind_at_point_time(ds, lat, lon, step_index, minutes):
    p0 = ds.isel(step=step_index).interp(latitude=lat, longitude=lon)
    p1 = ds.isel(step=step_index + 1).interp(latitude=lat, longitude=lon)

    u0 = float(p0["u10"])
    v0 = float(p0["v10"])
    u1 = float(p1["u10"])
    v1 = float(p1["v10"])

    step_minutes = int(
        (ds["step"][step_index + 1] - ds["step"][step_index])
        .astype("timedelta64[m]")
        / np.timedelta64(1, "m")
    )

    alpha = minutes / step_minutes
    u, v = interpolate_uv(u0, v0, u1, v1, alpha)

    tws, twd = uv_to_tws_twd(u, v)

    return {"u": round(u, 3), "v": round(v, 3), "tws": round(tws, 2), "twd": round(twd, 1)}
