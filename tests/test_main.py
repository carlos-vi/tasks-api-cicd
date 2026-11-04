def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_tasks(client):
    response = client.post("/tasks", json={"title": "Learn CI/CD"})
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "Learn CI/CD"
    assert isinstance(created["id"], int)

    response = client.get("/tasks")
    assert {"id": created["id"], "title": "Learn CI/CD"} in response.json()


def test_title_validation(client):
    assert client.post("/tasks", json={"title": ""}).status_code == 422
    assert client.post("/tasks", json={"title": "x" * 201}).status_code == 422
    assert client.post("/tasks", json={"title": "x" * 200}).status_code == 201


def test_web_ui_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>Tasks</title>" in response.text

    assert client.get("/app.js").status_code == 200
    assert client.get("/style.css").status_code == 200


def test_api_routes_still_take_priority_over_static_files(client):
    # The UI is mounted at "/", but it must not shadow the API or its documentation
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/tasks").headers["content-type"].startswith("application/json")
    assert client.get("/docs").status_code == 200


def test_ids_are_unique(client):
    first = client.post("/tasks", json={"title": "one"}).json()
    second = client.post("/tasks", json={"title": "two"}).json()
    assert first["id"] != second["id"]
