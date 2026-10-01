def test_register_and_login_flow(client):
    # 1. Register new user
    reg_data = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "Password123",
    }
    reg_res = client.post("/api/auth/register", json=reg_data)
    assert reg_res.status_code == 200
    token_data = reg_res.json()
    assert "access_token" in token_data
    assert token_data["user"]["email"] == "newuser@example.com"
    token = token_data["access_token"]

    # 2. Get me with token
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "newuser@example.com"

    # 3. Login
    login_res = client.post("/api/auth/login", json={"email": "newuser@example.com", "password": "Password123"})
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_login_invalid_password(client, test_admin_user):
    res = client.post("/api/auth/login", json={"email": test_admin_user.email, "password": "WrongPassword"})
    assert res.status_code == 401


def test_access_protected_endpoint_without_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
