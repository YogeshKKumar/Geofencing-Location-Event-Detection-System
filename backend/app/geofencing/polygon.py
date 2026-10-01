from typing import List, Tuple
import math
from app.geofencing.utils import point_to_segment_distance
from app.core.config import settings

try:
    from shapely.geometry import Point, Polygon
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False


def ray_casting_point_in_polygon(lat: float, lon: float, poly_points: List[Tuple[float, float]]) -> bool:
    """
    Standard Ray Casting algorithm (Jordan curve theorem) in pure Python.
    Points are (latitude, longitude).
    """
    n = len(poly_points)
    if n < 3:
        return False

    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly_points[i][0], poly_points[i][1]  # lat, lon
        xj, yj = poly_points[j][0], poly_points[j][1]

        # Check if point lies directly on edge segment
        if min(xi, xj) <= lat <= max(xi, xj) and min(yi, yj) <= lon <= max(yi, yj):
            cross = (lat - xi) * (yj - yi) - (lon - yi) * (xj - xi)
            if abs(cross) < 1e-9:
                return True

        if (xi > lat) != (xj > lat):
            inters_lon = (yj - yi) * (lat - xi) / (xj - xi) + yi
            if lon < inters_lon:
                inside = not inside

        j = i

    return inside


def min_distance_to_polygon_edges(lat: float, lon: float, poly_points: List[Tuple[float, float]]) -> float:
    """
    Compute shortest distance in meters from point P to any edge of the polygon.
    """
    n = len(poly_points)
    if n < 2:
        return float("inf")

    min_dist = float("inf")
    for i in range(n):
        p1 = poly_points[i]
        p2 = poly_points[(i + 1) % n]
        d = point_to_segment_distance(lat, lon, p1[0], p1[1], p2[0], p2[1])
        if d < min_dist:
            min_dist = d

    return min_dist


def is_inside_polygon(
    point_lat: float,
    point_lon: float,
    polygon_points: List[Tuple[float, float]],
    accuracy_meters: float = 0.0,
    previous_state: str = "UNKNOWN",
    boundary_buffer: float = settings.BOUNDARY_BUFFER_METERS,
    accuracy_threshold: float = settings.GPS_ACCURACY_THRESHOLD,
) -> bool:
    """
    Determine if a point (lat, lon) is inside a polygon defined by [(lat, lon), ...].
    Applies Shapely when available with ray casting fallback, plus GPS accuracy and hysteresis.
    """
    if len(polygon_points) < 3:
        return False

    # Check accuracy threshold
    if accuracy_meters > accuracy_threshold and previous_state in ("INSIDE", "OUTSIDE"):
        return previous_state == "INSIDE"

    is_raw_inside = False
    if HAS_SHAPELY:
        try:
            # In Shapely: x = longitude, y = latitude
            shapely_poly = Polygon([(p[1], p[0]) for p in polygon_points])
            if not shapely_poly.is_valid:
                shapely_poly = shapely_poly.buffer(0)
            pt = Point(point_lon, point_lat)
            is_raw_inside = shapely_poly.covers(pt) or shapely_poly.contains(pt)
        except Exception:
            is_raw_inside = ray_casting_point_in_polygon(point_lat, point_lon, polygon_points)
    else:
        is_raw_inside = ray_casting_point_in_polygon(point_lat, point_lon, polygon_points)

    if is_raw_inside:
        return True

    # If previous state was INSIDE and point is slightly outside, apply hysteresis buffer
    if previous_state == "INSIDE":
        edge_dist = min_distance_to_polygon_edges(point_lat, point_lon, polygon_points)
        effective_buffer = max(boundary_buffer, max(0.0, accuracy_meters))
        if edge_dist <= effective_buffer:
            return True

    return False
