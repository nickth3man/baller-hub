def test_list_awards(client_with_lifespan):
    response = client_with_lifespan.get("/api/v1/awards/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "name" in data[0]
        assert "award_id" in data[0]


def test_get_award_by_id(client_with_lifespan):
    # First get all awards to find a valid ID
    list_response = client_with_lifespan.get("/api/v1/awards/")
    awards = list_response.json()

    if len(awards) > 0:
        award_id = awards[0]["award_id"]
        response = client_with_lifespan.get(f"/api/v1/awards/{award_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["award_id"] == award_id
        assert "recipients" in data
        assert isinstance(data["recipients"], list)
    else:
        # If no data, 404 is acceptable for a specific ID
        response = client_with_lifespan.get("/api/v1/awards/1")
        assert response.status_code == 404
