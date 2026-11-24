from datetime import datetime, timezone


def test_create_task_success(client):
    project = client.post("/projects", json={"name": "Task Parent Project"}).json()
    project_id = project["id"]

    payload = {
        "title": "Design Database Schema",
        "description": "Create SQLAlchemy models and Alembic migrations",
        "status": "in_progress",
        "priority": "high",
        "due_date": "2026-12-01T12:00:00Z",
        "project_id": project_id,
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Design Database Schema"
    assert data["description"] == "Create SQLAlchemy models and Alembic migrations"
    assert data["status"] == "in_progress"
    assert data["priority"] == "high"
    assert data["project_id"] == project_id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_default_values(client):
    project = client.post("/projects", json={"name": "Defaults Project"}).json()

    payload = {
        "title": "Default Task",
        "project_id": project["id"],
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "todo"
    assert data["priority"] == "medium"
    assert data["description"] is None
    assert data["due_date"] is None


def test_create_task_invalid_project(client):
    payload = {
        "title": "Orphan Task",
        "project_id": 99999,
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 404
    assert "Project with id 99999 does not exist" in response.json()["detail"]


def test_create_task_validation_error(client):
    # Empty title should fail
    response = client.post("/tasks", json={"title": "", "project_id": 1})
    assert response.status_code == 422

    # Invalid status should fail
    response = client.post(
        "/tasks",
        json={"title": "Task", "project_id": 1, "status": "not_a_valid_status"},
    )
    assert response.status_code == 422


def test_list_tasks_and_filtering(client):
    p1 = client.post("/projects", json={"name": "P1"}).json()["id"]
    p2 = client.post("/projects", json={"name": "P2"}).json()["id"]

    client.post("/tasks", json={"title": "T1", "project_id": p1, "status": "todo", "priority": "low"})
    client.post("/tasks", json={"title": "T2", "project_id": p1, "status": "in_progress", "priority": "high"})
    client.post("/tasks", json={"title": "T3", "project_id": p2, "status": "done", "priority": "high"})

    # All tasks
    res_all = client.get("/tasks")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 3

    # Filter by project_id
    res_p1 = client.get(f"/tasks?project_id={p1}")
    assert res_p1.status_code == 200
    assert len(res_p1.json()) == 2

    # Filter by status
    res_status = client.get("/tasks?status=in_progress")
    assert res_status.status_code == 200
    assert len(res_status.json()) == 1
    assert res_status.json()[0]["title"] == "T2"

    # Filter by priority
    res_priority = client.get("/tasks?priority=high")
    assert res_priority.status_code == 200
    assert len(res_priority.json()) == 2


def test_get_task_by_id(client):
    p = client.post("/projects", json={"name": "P"}).json()["id"]
    t = client.post("/tasks", json={"title": "Specific Task", "project_id": p}).json()
    task_id = t["id"]

    res = client.get(f"/tasks/{task_id}")
    assert res.status_code == 200
    assert res.json()["title"] == "Specific Task"


def test_get_task_not_found(client):
    res = client.get("/tasks/99999")
    assert res.status_code == 404
    assert "Task with id 99999 not found" in res.json()["detail"]


def test_update_task(client):
    p = client.post("/projects", json={"name": "P"}).json()["id"]
    t = client.post("/tasks", json={"title": "Old Title", "project_id": p}).json()
    task_id = t["id"]

    update_payload = {
        "title": "New Title",
        "status": "done",
        "priority": "low",
        "description": "Now finished",
    }
    res = client.patch(f"/tasks/{task_id}", json=update_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "New Title"
    assert data["status"] == "done"
    assert data["priority"] == "low"
    assert data["description"] == "Now finished"


def test_update_task_not_found(client):
    res = client.patch("/tasks/99999", json={"title": "Updated"})
    assert res.status_code == 404


def test_delete_task(client):
    p = client.post("/projects", json={"name": "P"}).json()["id"]
    t = client.post("/tasks", json={"title": "To Delete", "project_id": p}).json()
    task_id = t["id"]

    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 404


def test_delete_task_not_found(client):
    del_res = client.delete("/tasks/99999")
    assert del_res.status_code == 404
