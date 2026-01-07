import math

EARTH_RADIUS_M = 6371000  # mètres
KNOT_TO_MS = 0.514444


def advance_position(lat, lon, heading_deg, speed_knots, duration_sec):
    """
    Avance une position GPS avec cap et vitesse constants
    """
    speed_ms = speed_knots * KNOT_TO_MS
    distance = speed_ms * duration_sec  # mètres

    heading = math.radians(heading_deg)

    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    dlat = (distance * math.cos(heading)) / EARTH_RADIUS_M
    dlon = (distance * math.sin(heading)) / (EARTH_RADIUS_M * math.cos(lat_rad))

    new_lat = lat_rad + dlat
    new_lon = lon_rad + dlon

    return (
        math.degrees(new_lat),
        math.degrees(new_lon)
    )
