USER_ID = "test-user-uuid"
HEADERS = {"X-User-Id": USER_ID}


def test_get_progress_empty(client, sample_points):
    resp = client.get("/api/progress", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


def test_update_mastery(client, sample_points):
    resp = client.put(
        "/api/progress/1",
        json={"mastery": "mastered"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["mastery"] == "mastered"
    assert resp.json()["review_count"] == 1


def test_update_mastery_increments_review_count(client, sample_points):
    client.put("/api/progress/1", json={"mastery": "partial"}, headers=HEADERS)
    resp = client.put("/api/progress/1", json={"mastery": "mastered"}, headers=HEADERS)
    assert resp.json()["review_count"] == 2


def test_get_progress_after_update(client, sample_points):
    client.put("/api/progress/1", json={"mastery": "mastered"}, headers=HEADERS)
    resp = client.get("/api/progress", headers=HEADERS)
    data = resp.json()
    assert len(data) == 1
    assert data[0]["point_id"] == 1
    assert data[0]["mastery"] == "mastered"


def test_toggle_favorite(client, sample_points):
    resp = client.put(
        "/api/progress/1/favorite",
        json={"is_favorite": True},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["is_favorite"] is True


def test_toggle_favorite_off(client, sample_points):
    client.put("/api/progress/1/favorite", json={"is_favorite": True}, headers=HEADERS)
    resp = client.put("/api/progress/1/favorite", json={"is_favorite": False}, headers=HEADERS)
    assert resp.json()["is_favorite"] is False


def test_progress_requires_user_id(client, sample_points):
    resp = client.get("/api/progress")
    assert resp.status_code == 400
