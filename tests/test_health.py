
def test_check_server_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["health"] == "ok"