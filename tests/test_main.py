from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_tasks():
    response = client.post("/tasks", json={"title": "Aprender CI/CD"})
    assert response.status_code == 201
    assert response.json()["title"] == "Aprender CI/CD"

    response = client.get("/tasks")
    assert any(t["title"] == "Aprender CI/CD" for t in response.json())
