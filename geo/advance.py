import math

EARTH_RADIUS_NM = 3440.065  # Rayon de la Terre en milles nautiques

def advance(lat, lon, course_deg, distance_nm):
    """
    Avance un point (lat, lon) d'une distance donnée sur un cap donné
    """
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    course = math.radians(course_deg)

    d = distance_nm / EARTH_RADIUS_NM

    lat2 = math.asin(
        math.sin(lat1) * math.cos(d)
        + math.cos(lat1) * math.sin(d) * math.cos(course)
    )

    lon2 = lon1 + math.atan2(
        math.sin(course) * math.sin(d) * math.cos(lat1),
        math.cos(d) - math.sin(lat1) * math.sin(lat2)
    )

    return math.degrees(lat2), math.degrees(lon2)
