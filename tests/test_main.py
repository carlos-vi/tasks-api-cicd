def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_tasks(client):
    response = client.post("/tasks", json={"title": "Aprender CI/CD"})
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "Aprender CI/CD"
    assert isinstance(created["id"], int)

    response = client.get("/tasks")
    assert {"id": created["id"], "title": "Aprender CI/CD"} in response.json()


def test_ids_are_unique(client):
    first = client.post("/tasks", json={"title": "una"}).json()
    second = client.post("/tasks", json={"title": "dos"}).json()
    assert first["id"] != second["id"]
