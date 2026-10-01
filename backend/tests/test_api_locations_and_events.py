from datetime import datetime, timezone, timedelta


def test_full_location_event_lifecycle(client, admin_token, test_regular_user):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create Geofence: Center (11.0168, 76.9558), radius 500 meters
    circle_res = client.post(
        "/api/geofences",
        json={
            "name": "E2E Office Geofence",
            "type": "CIRCLE",
            "center_latitude": 11.0168,
            "center_longitude": 76.9558,
            "radius_meters": 500.0,
            "is_active": True,
        },
        headers=headers,
    )
    assert circle_res.status_code == 201
    geo_id = circle_res.json()["id"]

    # 2. Create Device
    dev_res = client.post(
        "/api/devices",
        json={
            "device_identifier": "E2E-DEV-001",
            "name": "Tracker Alpha",
            "user_id": test_regular_user.id,
            "is_active": True,
        },
        headers=headers,
    )
    assert dev_res.status_code == 201
    dev_id = dev_res.json()["id"]

    base_time = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)

    # 3. Location 1: OUTSIDE (~3.5km away)
    loc1_res = client.post(
        "/api/locations",
        json={
            "device_id": dev_id,
            "latitude": 11.0500,
            "longitude": 76.9558,
            "accuracy_meters": 5.0,
            "timestamp": (base_time).isoformat(),
        },
    )
    assert loc1_res.status_code == 200
    # No ENTER event should be generated
    events_1 = loc1_res.json()["events"]
    assert not any(e["event_type"] == "ENTER" for e in events_1)

    # 4. Location 2: INSIDE (at center)
    loc2_res = client.post(
        "/api/locations",
        json={
            "device_id": dev_id,
            "latitude": 11.0168,
            "longitude": 76.9558,
            "accuracy_meters": 5.0,
            "timestamp": (base_time + timedelta(seconds=10)).isoformat(),
        },
    )
    assert loc2_res.status_code == 200
    events_2 = loc2_res.json()["events"]
    enter_events = [e for e in events_2 if e["geofence_id"] == geo_id and e["event_type"] == "ENTER"]
    assert len(enter_events) == 1
    assert enter_events[0]["previous_state"] == "OUTSIDE"
    assert enter_events[0]["current_state"] == "INSIDE"

    # 5. Location 3: Second INSIDE (~50m from center)
    loc3_res = client.post(
        "/api/locations",
        json={
            "device_id": dev_id,
            "latitude": 11.0170,
            "longitude": 76.9559,
            "accuracy_meters": 5.0,
            "timestamp": (base_time + timedelta(seconds=20)).isoformat(),
        },
    )
    assert loc3_res.status_code == 200
    events_3 = loc3_res.json()["events"]
    # Should NOT generate another ENTER event!
    assert not any(e["event_type"] == "ENTER" for e in events_3)

    # 6. Location 4: OUTSIDE (~3.5km away)
    loc4_res = client.post(
        "/api/locations",
        json={
            "device_id": dev_id,
            "latitude": 11.0500,
            "longitude": 76.9558,
            "accuracy_meters": 5.0,
            "timestamp": (base_time + timedelta(seconds=30)).isoformat(),
        },
    )
    assert loc4_res.status_code == 200
    events_4 = loc4_res.json()["events"]
    exit_events = [e for e in events_4 if e["geofence_id"] == geo_id and e["event_type"] == "EXIT"]
    assert len(exit_events) == 1
    assert exit_events[0]["previous_state"] == "INSIDE"
    assert exit_events[0]["current_state"] == "OUTSIDE"

    # 7. Location 5: Repeated OUTSIDE
    loc5_res = client.post(
        "/api/locations",
        json={
            "device_id": dev_id,
            "latitude": 11.0550,
            "longitude": 76.9558,
            "accuracy_meters": 5.0,
            "timestamp": (base_time + timedelta(seconds=40)).isoformat(),
        },
    )
    assert loc5_res.status_code == 200
    events_5 = loc5_res.json()["events"]
    # Should NOT generate another EXIT event!
    assert not any(e["event_type"] == "EXIT" for e in events_5)

    # 8. Query Event History
    ev_hist_res = client.get(f"/api/events?device_id={dev_id}", headers=headers)
    assert ev_hist_res.status_code == 200
    recorded_events = ev_hist_res.json()["data"]
    event_types = [e["event_type"] for e in recorded_events]
    assert "ENTER" in event_types
    assert "EXIT" in event_types

    # 9. Query Location History
    loc_hist_res = client.get(f"/api/locations?device_id={dev_id}", headers=headers)
    assert loc_hist_res.status_code == 200
    assert len(loc_hist_res.json()["data"]) >= 4
