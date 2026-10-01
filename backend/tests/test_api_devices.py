def test_create_and_list_devices(client, admin_token, test_regular_user):
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Register device
    dev_payload = {
        "device_identifier": "DEV-TEST-001",
        "name": "Fleet Van 1",
        "user_id": test_regular_user.id,
        "is_active": True,
    }
    create_res = client.post("/api/devices", json=dev_payload, headers=headers)
    assert create_res.status_code == 201
    dev_data = create_res.json()
    assert dev_data["device_identifier"] == "DEV-TEST-001"
    dev_id = dev_data["id"]

    # List devices
    list_res = client.get("/api/devices", headers=headers)
    assert list_res.status_code == 200
    assert any(d["id"] == dev_id for d in list_res.json()["data"])

    # Update status
    patch_res = client.patch(f"/api/devices/{dev_id}/status", json={"is_active": False}, headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["is_active"] is False


def test_duplicate_device_identifier_rejected(client, admin_token, test_regular_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    dev_payload = {
        "device_identifier": "DEV-UNIQUE-X",
        "name": "Original Device",
        "user_id": test_regular_user.id,
    }
    res1 = client.post("/api/devices", json=dev_payload, headers=headers)
    assert res1.status_code == 201

    # Attempt second device with same identifier
    res2 = client.post("/api/devices", json=dev_payload, headers=headers)
    assert res2.status_code == 409
