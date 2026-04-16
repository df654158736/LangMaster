USER_ID = "test-user-uuid"
HEADERS = {"X-User-Id": USER_ID}


def test_dashboard_empty(client, sample_points):
    resp = client.get("/api/stats/dashboard", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_points"] == 3
    assert data["mastered_count"] == 0
    assert data["interview_count"] == 0
    assert data["weak_count"] == 0
    assert data["last_score_percent"] is None


def test_dashboard_with_progress(client, sample_points):
    client.put("/api/progress/1", json={"mastery": "mastered"}, headers=HEADERS)
    client.put("/api/progress/2", json={"mastery": "partial"}, headers=HEADERS)
    resp = client.get("/api/stats/dashboard", headers=HEADERS)
    data = resp.json()
    assert data["mastered_count"] == 1
    assert data["weak_count"] == 1  # partial counts as weak


def test_dashboard_with_interview(client, sample_points):
    client.post(
        "/api/interview/start",
        json={"count": 2, "strategy": "random"},
        headers=HEADERS,
    )
    resp = client.get("/api/stats/dashboard", headers=HEADERS)
    assert resp.json()["interview_count"] == 1


def test_weak_points_empty(client, sample_points):
    resp = client.get("/api/stats/weak-points", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


def test_weak_points_returns_partial_and_not_started_reviewed(client, sample_points):
    client.put("/api/progress/1", json={"mastery": "mastered"}, headers=HEADERS)
    client.put("/api/progress/2", json={"mastery": "partial"}, headers=HEADERS)
    resp = client.get("/api/stats/weak-points", headers=HEADERS)
    data = resp.json()
    assert len(data) == 1
    assert data[0]["point_id"] == 2
    assert data[0]["mastery"] == "partial"
