import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
from app.schemas.location import LocationInput
from app.schemas.geofence import GeofenceCreate, PointSchema
from app.geofencing.utils import haversine_distance


def test_haversine_distance_zero():
    dist = haversine_distance(11.0168, 76.9558, 11.0168, 76.9558)
    assert dist == 0.0


def test_haversine_distance_known_points():
    # London to Paris: roughly 343 km (340,000 - 350,000 meters)
    london_lat, london_lon = 51.5074, -0.1278
    paris_lat, paris_lon = 48.8566, 2.3522
    dist = haversine_distance(london_lat, london_lon, paris_lat, paris_lon)
    assert 340000 < dist < 350000


def test_valid_coordinates():
    loc = LocationInput(
        device_id=1,
        latitude=11.0168,
        longitude=76.9558,
        accuracy_meters=10.0,
    )
    assert loc.latitude == 11.0168
    assert loc.longitude == 76.9558


def test_invalid_latitude_high():
    with pytest.raises(ValidationError):
        LocationInput(
            device_id=1,
            latitude=95.0,  # Invalid: > 90
            longitude=76.9558,
        )


def test_invalid_latitude_low():
    with pytest.raises(ValidationError):
        LocationInput(
            device_id=1,
            latitude=-91.0,  # Invalid: < -90
            longitude=76.9558,
        )


def test_invalid_longitude_high():
    with pytest.raises(ValidationError):
        LocationInput(
            device_id=1,
            latitude=11.0,
            longitude=181.0,  # Invalid: > 180
        )


def test_invalid_longitude_low():
    with pytest.raises(ValidationError):
        LocationInput(
            device_id=1,
            latitude=11.0,
            longitude=-185.0,  # Invalid: < -180
        )


def test_negative_accuracy_rejected():
    with pytest.raises(ValidationError):
        LocationInput(
            device_id=1,
            latitude=11.0,
            longitude=76.0,
            accuracy_meters=-5.0,
        )


def test_future_timestamp_rejected():
    future_time = datetime.now(timezone.utc) + timedelta(days=2)
    with pytest.raises(ValidationError):
        LocationInput(
            device_id=1,
            latitude=11.0,
            longitude=76.0,
            timestamp=future_time,
        )


def test_circle_radius_gt_zero():
    with pytest.raises(ValidationError):
        GeofenceCreate(
            name="Invalid Circle",
            type="CIRCLE",
            center_latitude=11.0,
            center_longitude=76.0,
            radius_meters=-10.0,  # Must be > 0
        )
