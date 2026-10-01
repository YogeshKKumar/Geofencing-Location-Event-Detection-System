import math
from typing import Tuple

EARTH_RADIUS_METERS = 6371000.0  # WGS-84 mean radius in meters


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the Earth (specified in decimal degrees) using Haversine formula.
    Returns distance in meters.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    # Clip to [0, 1] to avoid math domain errors due to floating point inaccuracies
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_METERS * c


def point_to_segment_distance(
    p_lat: float, p_lon: float,
    a_lat: float, a_lon: float,
    b_lat: float, b_lon: float
) -> float:
    """
    Calculate perpendicular distance from point P to line segment AB in meters.
    Approximated using equirectangular projection centered at P.
    """
    # Convert lat/lon differences to meters
    mid_lat = math.radians((a_lat + b_lat + p_lat) / 3.0)
    meters_per_deg_lat = 111132.954 - 559.822 * math.cos(2 * mid_lat)
    meters_per_deg_lon = 111412.84 * math.cos(mid_lat)

    px = (p_lon - a_lon) * meters_per_deg_lon
    py = (p_lat - a_lat) * meters_per_deg_lat

    bx = (b_lon - a_lon) * meters_per_deg_lon
    by = (b_lat - a_lat) * meters_per_deg_lat

    segment_len_sq = bx * bx + by * by
    if segment_len_sq == 0.0:
        return math.hypot(px, py)

    # Project point P onto segment AB, parameter t clamped to [0, 1]
    t = max(0.0, min(1.0, (px * bx + py * by) / segment_len_sq))

    proj_x = t * bx
    proj_y = t * by

    return math.hypot(px - proj_x, py - proj_y)
