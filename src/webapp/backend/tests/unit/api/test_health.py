def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
