from datetime import timedelta

from app.core.security import create_access_token


def test_register_success(client):
    payload = {
        "email": "newuser@example.com",
        "password": "strongpassword123",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "password_hash" not in data


def test_register_duplicate_email(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "anotherpassword",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_validation_error(client):
    # Invalid email
    res1 = client.post("/auth/register", json={"email": "notanemail", "password": "validpassword"})
    assert res1.status_code == 422

    # Short password (< 6 chars)
    res2 = client.post("/auth/register", json={"email": "valid@example.com", "password": "123"})
    assert res2.status_code == 422


def test_login_success(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "password123",
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


def test_login_wrong_password(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "wrongpassword",
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    payload = {
        "email": "ghost@example.com",
        "password": "password123",
    }
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401


def test_get_me_success(client, auth_headers, test_user):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_get_me_unauthenticated(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_me_invalid_token(client):
    headers = {"Authorization": "Bearer invalid.token.value"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_get_me_expired_token(client, test_user):
    expired_token = create_access_token(
        subject=test_user.id,
        expires_delta=timedelta(seconds=-10),
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]
