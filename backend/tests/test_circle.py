from app.geofencing.circle import is_inside_circle
from app.geofencing.utils import haversine_distance

CENTER_LAT = 11.0168
CENTER_LON = 76.9558
RADIUS = 500.0  # 500 meters


def test_circle_center_point():
    assert is_inside_circle(CENTER_LAT, CENTER_LON, CENTER_LAT, CENTER_LON, RADIUS) is True


def test_circle_inside_point():
    # Point ~100m away
    # 0.0009 degrees latitude is approx 100 meters
    inside_lat = CENTER_LAT + 0.0009
    inside_lon = CENTER_LON
    dist = haversine_distance(CENTER_LAT, CENTER_LON, inside_lat, inside_lon)
    assert dist < RADIUS
    assert is_inside_circle(inside_lat, inside_lon, CENTER_LAT, CENTER_LON, RADIUS) is True


def test_circle_outside_point():
    # Point ~1km away
    outside_lat = CENTER_LAT + 0.01
    outside_lon = CENTER_LON
    dist = haversine_distance(CENTER_LAT, CENTER_LON, outside_lat, outside_lon)
    assert dist > RADIUS
    assert is_inside_circle(outside_lat, outside_lon, CENTER_LAT, CENTER_LON, RADIUS) is False


def test_circle_exact_boundary():
    # Construct a point close to radius
    lat = CENTER_LAT + 0.0044966
    dist = haversine_distance(CENTER_LAT, CENTER_LON, lat, CENTER_LON)
    # Check boundary behavior
    inside = is_inside_circle(lat, CENTER_LON, CENTER_LAT, CENTER_LON, dist + 0.1)
    assert inside is True


def test_circle_hysteresis_when_inside():
    # When previous_state is INSIDE, device at 505m with boundary_buffer=10m stays INSIDE
    # Radius = 500m. 0.00455 deg latitude is ~506m
    border_lat = CENTER_LAT + 0.00455
    dist = haversine_distance(CENTER_LAT, CENTER_LON, border_lat, CENTER_LON)
    assert 500.0 < dist <= 510.0

    # If previously OUTSIDE, it is strictly outside
    assert is_inside_circle(border_lat, CENTER_LON, CENTER_LAT, CENTER_LON, RADIUS, previous_state="OUTSIDE", boundary_buffer=10.0) is False

    # If previously INSIDE, hysteresis buffer keeps it INSIDE (prevents jitter oscillation)
    assert is_inside_circle(border_lat, CENTER_LON, CENTER_LAT, CENTER_LON, RADIUS, previous_state="INSIDE", boundary_buffer=15.0) is True


def test_circle_gps_accuracy_threshold():
    # When accuracy is worse than threshold (e.g. 150m > 100m), maintains previous state
    far_lat = CENTER_LAT + 0.02
    assert is_inside_circle(far_lat, CENTER_LON, CENTER_LAT, CENTER_LON, RADIUS, accuracy_meters=150.0, previous_state="INSIDE", accuracy_threshold=100.0) is True
