def test_list_points_returns_all(client, sample_points):
    resp = client.get("/api/points")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3


def test_list_points_filter_by_category(client, sample_points):
    resp = client.get("/api/points?category=Prompt")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "ChatPromptTemplate"


def test_list_points_filter_by_level(client, sample_points):
    resp = client.get("/api/points?level=basic")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_list_points_sort_by_interview_heat(client, sample_points):
    resp = client.get("/api/points?sort=interview_heat")
    assert resp.status_code == 200
    data = resp.json()
    # All have heat=3, so sort is stable by sort_order
    assert data[0]["title"] == "ChatPromptTemplate"


def test_list_points_sort_by_dev_utility(client, sample_points):
    resp = client.get("/api/points?sort=dev_utility")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_get_point_detail(client, sample_points):
    resp = client.get("/api/points/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "ChatPromptTemplate"
    assert "code_example" in data
    assert len(data["key_points"]) == 3


def test_get_point_not_found(client, sample_points):
    resp = client.get("/api/points/999")
    assert resp.status_code == 404
