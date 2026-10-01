from app.geofencing.utils import haversine_distance
from app.core.config import settings


def is_inside_circle(
    point_lat: float,
    point_lon: float,
    center_lat: float,
    center_lon: float,
    radius_meters: float,
    accuracy_meters: float = 0.0,
    previous_state: str = "UNKNOWN",
    boundary_buffer: float = settings.BOUNDARY_BUFFER_METERS,
    accuracy_threshold: float = settings.GPS_ACCURACY_THRESHOLD,
) -> bool:
    """
    Determine if a point is inside a circular geofence with GPS accuracy and hysteresis.

    Hysteresis Strategy:
    - If previous_state is 'INSIDE':
      We avoid premature EXIT by applying an exit buffer:
      effective_exit_radius = radius_meters + max(boundary_buffer, max(0.0, accuracy_meters))
      Inside if: distance <= effective_exit_radius.
    - If previous_state is 'OUTSIDE' or 'UNKNOWN':
      Enter geofence strictly when: distance <= radius_meters.
    """
    distance = haversine_distance(point_lat, point_lon, center_lat, center_lon)

    # If accuracy exceeds threshold, GPS is degraded; maintain previous state if known
    if accuracy_meters > accuracy_threshold and previous_state in ("INSIDE", "OUTSIDE"):
        return previous_state == "INSIDE"

    if previous_state == "INSIDE":
        # Hysteresis buffer to prevent noise oscillation
        effective_radius = radius_meters + max(boundary_buffer, max(0.0, accuracy_meters))
        return distance <= effective_radius
    else:
        # Strict boundary for entering
        return distance <= radius_meters
