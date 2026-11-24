def test_tasks_unauthenticated(client):
    assert client.get("/tasks").status_code == 401
    assert client.post("/tasks", json={"title": "T", "project_id": 1}).status_code == 401
    assert client.get("/tasks/1").status_code == 401
    assert client.patch("/tasks/1", json={"title": "T2"}).status_code == 401
    assert client.delete("/tasks/1").status_code == 401


def test_create_task_success(client, auth_headers):
    project = client.post("/projects", json={"name": "Task Parent Project"}, headers=auth_headers).json()
    project_id = project["id"]

    payload = {
        "title": "Design Database Schema",
        "description": "Create SQLAlchemy models and Alembic migrations",
        "status": "in_progress",
        "priority": "high",
        "due_date": "2026-12-01T12:00:00Z",
        "project_id": project_id,
    }
    response = client.post("/tasks", json=payload, headers=auth_headers)
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


def test_create_task_default_values(client, auth_headers):
    project = client.post("/projects", json={"name": "Defaults Project"}, headers=auth_headers).json()

    payload = {
        "title": "Default Task",
        "project_id": project["id"],
    }
    response = client.post("/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "todo"
    assert data["priority"] == "medium"
    assert data["description"] is None
    assert data["due_date"] is None


def test_create_task_invalid_project(client, auth_headers):
    payload = {
        "title": "Orphan Task",
        "project_id": 99999,
    }
    response = client.post("/tasks", json=payload, headers=auth_headers)
    assert response.status_code == 404
    assert "Project with id 99999 does not exist" in response.json()["detail"]


def test_create_task_validation_error(client, auth_headers):
    # Empty title should fail
    response = client.post("/tasks", json={"title": "", "project_id": 1}, headers=auth_headers)
    assert response.status_code == 422

    # Invalid status should fail
    response = client.post(
        "/tasks",
        json={"title": "Task", "project_id": 1, "status": "not_a_valid_status"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_list_tasks_and_filtering(client, auth_headers):
    p1 = client.post("/projects", json={"name": "P1"}, headers=auth_headers).json()["id"]
    p2 = client.post("/projects", json={"name": "P2"}, headers=auth_headers).json()["id"]

    client.post("/tasks", json={"title": "T1", "project_id": p1, "status": "todo", "priority": "low"}, headers=auth_headers)
    client.post("/tasks", json={"title": "T2", "project_id": p1, "status": "in_progress", "priority": "high"}, headers=auth_headers)
    client.post("/tasks", json={"title": "T3", "project_id": p2, "status": "done", "priority": "high"}, headers=auth_headers)

    # All tasks
    res_all = client.get("/tasks", headers=auth_headers)
    assert res_all.status_code == 200
    assert len(res_all.json()) == 3

    # Filter by project_id
    res_p1 = client.get(f"/tasks?project_id={p1}", headers=auth_headers)
    assert res_p1.status_code == 200
    assert len(res_p1.json()) == 2

    # Filter by status
    res_status = client.get("/tasks?status=in_progress", headers=auth_headers)
    assert res_status.status_code == 200
    assert len(res_status.json()) == 1
    assert res_status.json()[0]["title"] == "T2"

    # Filter by priority
    res_priority = client.get("/tasks?priority=high", headers=auth_headers)
    assert res_priority.status_code == 200
    assert len(res_priority.json()) == 2


def test_get_task_by_id(client, auth_headers):
    p = client.post("/projects", json={"name": "P"}, headers=auth_headers).json()["id"]
    t = client.post("/tasks", json={"title": "Specific Task", "project_id": p}, headers=auth_headers).json()
    task_id = t["id"]

    res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Specific Task"


def test_get_task_not_found(client, auth_headers):
    res = client.get("/tasks/99999", headers=auth_headers)
    assert res.status_code == 404
    assert "Task with id 99999 not found" in res.json()["detail"]


def test_update_task(client, auth_headers):
    p = client.post("/projects", json={"name": "P"}, headers=auth_headers).json()["id"]
    t = client.post("/tasks", json={"title": "Old Title", "project_id": p}, headers=auth_headers).json()
    task_id = t["id"]

    update_payload = {
        "title": "New Title",
        "status": "done",
        "priority": "low",
        "description": "Now finished",
    }
    res = client.patch(f"/tasks/{task_id}", json=update_payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "New Title"
    assert data["status"] == "done"
    assert data["priority"] == "low"
    assert data["description"] == "Now finished"


def test_update_task_not_found(client, auth_headers):
    res = client.patch("/tasks/99999", json={"title": "Updated"}, headers=auth_headers)
    assert res.status_code == 404


def test_delete_task(client, auth_headers):
    p = client.post("/projects", json={"name": "P"}, headers=auth_headers).json()["id"]
    t = client.post("/tasks", json={"title": "To Delete", "project_id": p}, headers=auth_headers).json()
    task_id = t["id"]

    del_res = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_res.status_code == 404


def test_delete_task_not_found(client, auth_headers):
    del_res = client.delete("/tasks/99999", headers=auth_headers)
    assert del_res.status_code == 404
