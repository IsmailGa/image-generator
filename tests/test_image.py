import pytest

def make_headers(client, email: str) -> dict:
    password = "correct-password"
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def test_create_image_defaults(auth_client):
    r = auth_client.post("/images", json={})
    assert r.status_code == 201
    data = r.json()
    assert data["width"] == 256
    assert data["height"] == 256
    assert data["kind"] == "noise"
    assert isinstance(data["seed"], int)

def test_get_missing_image_return_404(auth_client):
    r = auth_client.get("/images/99999")
    assert r.status_code == 404

@pytest.mark.parametrize(
    "payload",
    [{"width": 0}, {"width": 2000}, {"height": -1}, {"kind": "banana"}],
)
def test_create_image_validation(auth_client, payload):
    r = auth_client.post("/images", json=payload)
    assert r.status_code == 422

def test_same_seed_gives_same_png(auth_client):
    created = auth_client.post("/images", json={"seed": 1, "width": 16, "height": 16}).json()
    first = auth_client.get(f"/images/{created["id"]}/file")
    second = auth_client.get(f"/images/{created["id"]}/file")
    assert first.status_code == 200
    assert first.headers["content-type"] == "image/png"
    assert first.content.startswith(b"\x89PNG")
    assert first.content == second.content

def test_list_image_newest_first_and_limit(auth_client):
    ids = [auth_client.post("/images", json={"seed": i}).json()["id"] for i in range(3)]
    r = auth_client.get("/images", params={"limit": 2})
    assert r.status_code == 200
    assert [item["id"] for item in r.json()] == [ids[2], ids[1]]

def test_create_image_defaults_without_token(client):
    r = client.post("/images", json={})
    assert r.status_code == 401

def test_user_cannot_access_another_users_image(client):
    headers_a = make_headers(client, "a@example.com")
    headers_b = make_headers(client, "b@example.com")

    created = client.post("/images", json={}, headers=headers_a)
    assert created.status_code == 201
    image_id = created.json()["id"]

    assert client.get(f"/images/{image_id}", headers=headers_a).status_code == 200

    assert client.get(f"/images/{image_id}", headers=headers_b).status_code == 404
    assert client.get(f"/images/{image_id}/file", headers=headers_b).status_code == 404

def test_list_contains_only_own_images(client):
    headers_a = make_headers(client, "a@example.com")
    headers_b = make_headers(client, "b@example.com")

    id_a = client.post("/images", json={}, headers=headers_a).json()["id"]
    id_b = client.post("/images", json={}, headers=headers_b).json()["id"]

    r = client.get("/images", headers=headers_b)
    assert r.status_code == 200
    ids_b = [item["id"] for item in r.json()]
    assert id_b in ids_b    
    assert id_a not in ids_b