def test_list_drafts(client_with_lifespan):
    response = client_with_lifespan.get("/api/v1/drafts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "year" in data[0]
        assert "draft_id" in data[0]


def test_get_draft_by_year(client_with_lifespan):
    # First get all drafts to find a valid year
    list_response = client_with_lifespan.get("/api/v1/drafts/")
    drafts = list_response.json()

    if len(drafts) > 0:
        year = drafts[0]["year"]
        response = client_with_lifespan.get(f"/api/v1/drafts/{year}")
        assert response.status_code == 200
        data = response.json()
        assert data["year"] == year
        assert "picks" in data
        assert isinstance(data["picks"], list)
    else:
        # If no data, 404 is acceptable for a specific year
        response = client_with_lifespan.get("/api/v1/drafts/2024")
        assert response.status_code == 404
