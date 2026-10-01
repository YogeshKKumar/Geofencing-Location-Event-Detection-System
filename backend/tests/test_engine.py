from app.geofencing.engine import GeofencingEngine
from app.models.geofence import Geofence, GeofencePoint


def test_multiple_overlapping_geofences():
    # Setup two overlapping geofences: Circle and Polygon
    circle = Geofence(
        id=1,
        name="Circle 1",
        type="CIRCLE",
        center_latitude=10.0,
        center_longitude=10.0,
        radius_meters=1000.0,
        is_active=True,
    )

    polygon = Geofence(
        id=2,
        name="Polygon 1",
        type="POLYGON",
        is_active=True,
    )
    polygon.points = [
        GeofencePoint(latitude=9.99, longitude=9.99, point_order=0),
        GeofencePoint(latitude=10.01, longitude=9.99, point_order=1),
        GeofencePoint(latitude=10.01, longitude=10.01, point_order=2),
        GeofencePoint(latitude=9.99, longitude=10.01, point_order=3),
    ]

    engine = GeofencingEngine()

    # Point (10.0, 10.0) is inside BOTH circle and polygon
    # Previous state for both is OUTSIDE
    prev_states = {1: "OUTSIDE", 2: "OUTSIDE"}
    results = engine.evaluate_all(
        geofences=[circle, polygon],
        latitude=10.0,
        longitude=10.0,
        previous_states=prev_states,
    )

    assert len(results) == 2
    res_circle = next(r for r in results if r.geofence_id == 1)
    res_polygon = next(r for r in results if r.geofence_id == 2)

    assert res_circle.current_state == "INSIDE"
    assert res_circle.event_type == "ENTER"

    assert res_polygon.current_state == "INSIDE"
    assert res_polygon.event_type == "ENTER"


def test_inactive_geofence_ignored():
    inactive_circle = Geofence(
        id=99,
        name="Inactive Geofence",
        type="CIRCLE",
        center_latitude=10.0,
        center_longitude=10.0,
        radius_meters=1000.0,
        is_active=False,
    )
    engine = GeofencingEngine()
    results = engine.evaluate_all(
        geofences=[inactive_circle],
        latitude=10.0,
        longitude=10.0,
    )
    assert len(results) == 0
