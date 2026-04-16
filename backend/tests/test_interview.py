USER_ID = "test-user-uuid"
HEADERS = {"X-User-Id": USER_ID}


def test_start_interview_random(client, sample_points):
    resp = client.post(
        "/api/interview/start",
        json={"count": 2, "strategy": "random"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert len(data["questions"]) == 2


def test_start_interview_filter_by_category(client, sample_points):
    resp = client.post(
        "/api/interview/start",
        json={"categories": ["Prompt"], "count": 10, "strategy": "random"},
        headers=HEADERS,
    )
    data = resp.json()
    assert len(data["questions"]) == 1
    assert data["questions"][0]["category"] == "Prompt"


def test_start_interview_filter_by_level(client, sample_points):
    resp = client.post(
        "/api/interview/start",
        json={"levels": ["basic"], "count": 10, "strategy": "random"},
        headers=HEADERS,
    )
    data = resp.json()
    assert len(data["questions"]) == 2


def test_start_interview_filter_by_heat(client, sample_points):
    resp = client.post(
        "/api/interview/start",
        json={"min_heat": 3, "count": 10, "strategy": "random"},
        headers=HEADERS,
    )
    data = resp.json()
    assert len(data["questions"]) == 3  # all have heat=3


def test_submit_answer(client, sample_points):
    start = client.post(
        "/api/interview/start",
        json={"count": 3, "strategy": "random"},
        headers=HEADERS,
    )
    session_id = start.json()["session_id"]
    resp = client.post(
        f"/api/interview/{session_id}/answer",
        json={"point_id": 1, "self_score": "mastered"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["results_count"] == 1


def test_get_report(client, sample_points):
    start = client.post(
        "/api/interview/start",
        json={"count": 3, "strategy": "random"},
        headers=HEADERS,
    )
    session_id = start.json()["session_id"]
    client.post(f"/api/interview/{session_id}/answer", json={"point_id": 1, "self_score": "mastered"}, headers=HEADERS)
    client.post(f"/api/interview/{session_id}/answer", json={"point_id": 2, "self_score": "partial"}, headers=HEADERS)
    client.post(f"/api/interview/{session_id}/answer", json={"point_id": 3, "self_score": "unfamiliar"}, headers=HEADERS)

    resp = client.get(f"/api/interview/{session_id}/report", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_mastered"] == 1
    assert data["total_partial"] == 1
    assert data["total_unfamiliar"] == 1


def test_get_history(client, sample_points):
    client.post(
        "/api/interview/start",
        json={"count": 2, "strategy": "random"},
        headers=HEADERS,
    )
    resp = client.get("/api/interview/history", headers=HEADERS)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_start_interview_sequential(client, sample_points):
    resp = client.post(
        "/api/interview/start",
        json={"count": 3, "strategy": "sequential"},
        headers=HEADERS,
    )
    data = resp.json()
    orders = [q["sort_order"] for q in data["questions"]]
    assert orders == sorted(orders)
