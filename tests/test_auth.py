import pytest

EMAIL = "user1@example.com"
PASSWORD = "correct-password"


@pytest.fixture
def registered_user(client):
    r = client.post("/auth/register", json={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 201
    return {"email": EMAIL, "password": PASSWORD}


def login(client, email, password):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_register_returns_201_without_password_hash(client):
    r = client.post("/auth/register", json={"email": EMAIL, "password": PASSWORD})
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == EMAIL
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_duplicate_email_returns_409(client, registered_user):
    r = client.post("/auth/register", json=registered_user)
    assert r.status_code == 409


def test_register_short_password_returns_422(client):
    r = client.post("/auth/register", json={"email": EMAIL, "password": "short"})
    assert r.status_code == 422


def test_login_success_returns_token(client, registered_user):
    r = login(client, registered_user["email"], registered_user["password"])
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client, registered_user):
    r = login(client, registered_user["email"], "wrong-password")
    assert r.status_code == 401


def test_login_unknown_email_returns_401(client):
    r = login(client, "nobody@example.com", PASSWORD)
    assert r.status_code == 401


def test_me_without_token_returns_401(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_me_with_invalid_token_returns_401(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401


def test_me_with_token_returns_user(client, registered_user):
    token = login(client, registered_user["email"], registered_user["password"]).json()["access_token"]
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == registered_user["email"]