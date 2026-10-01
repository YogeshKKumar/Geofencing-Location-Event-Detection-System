def test_create_and_manage_circle_geofence(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create circular geofence
    circle_payload = {
        "name": "Test Office Circle",
        "description": "Office testing perimeter",
        "type": "CIRCLE",
        "center_latitude": 11.0168,
        "center_longitude": 76.9558,
        "radius_meters": 350.0,
        "is_active": True,
    }
    create_res = client.post("/api/geofences", json=circle_payload, headers=headers)
    assert create_res.status_code == 201
    geo_data = create_res.json()
    assert geo_data["name"] == "Test Office Circle"
    assert geo_data["radius_meters"] == 350.0
    geo_id = geo_data["id"]

    # Read back
    get_res = client.get(f"/api/geofences/{geo_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == geo_id

    # Toggle status
    patch_res = client.patch(f"/api/geofences/{geo_id}/status?is_active=false", json={"is_active": False}, headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["is_active"] is False

    # Delete
    del_res = client.delete(f"/api/geofences/{geo_id}", headers=headers)
    assert del_res.status_code == 200


def test_create_and_manage_polygon_geofence(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    poly_payload = {
        "name": "Test Warehouse Polygon",
        "description": "Warehouse polygon boundary",
        "type": "POLYGON",
        "is_active": True,
        "points": [
            {"latitude": 11.0160, "longitude": 76.9550},
            {"latitude": 11.0175, "longitude": 76.9550},
            {"latitude": 11.0175, "longitude": 76.9575},
            {"latitude": 11.0160, "longitude": 76.9575},
        ],
    }
    create_res = client.post("/api/geofences", json=poly_payload, headers=headers)
    assert create_res.status_code == 201
    poly_data = create_res.json()
    assert len(poly_data["points"]) == 4
    assert poly_data["type"] == "POLYGON"


def test_regular_user_cannot_create_geofence(client, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    circle_payload = {
        "name": "Unauthorized Circle",
        "type": "CIRCLE",
        "center_latitude": 11.0,
        "center_longitude": 76.0,
        "radius_meters": 100.0,
    }
    res = client.post("/api/geofences", json=circle_payload, headers=headers)
    assert res.status_code == 403
