from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_and_get_task():
    resp = client.post("/tasks", json={"title": "Test task"})
    assert resp.status_code == 201
    task_id = resp.json()["id"]

    resp = client.get(f"/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test task"


def test_get_nonexistent_task():
    resp = client.get("/tasks/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_update_task():
    created = client.post("/tasks", json={"title": "Old"}).json()
    resp = client.put(f"/tasks/{created['id']}", json={"title": "New"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"


def test_delete_task():
    created = client.post("/tasks", json={"title": "Delete me"}).json()
    resp = client.delete(f"/tasks/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/tasks/{created['id']}").status_code == 404