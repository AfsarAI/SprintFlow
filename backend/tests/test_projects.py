from app.models.user import User


def test_create_project_with_default_user(client):
    payload = {
        "name": "SprintFlow MVP",
        "description": "Initial SprintFlow development project",
    }
    response = client.post("/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "SprintFlow MVP"
    assert data["description"] == "Initial SprintFlow development project"
    assert "id" in data
    assert "owner_id" in data
    assert data["owner_id"] is not None
    assert "created_at" in data
    assert "updated_at" in data


def test_create_project_with_explicit_user(client, db_session):
    user = User(email="custom@sprintflow.local", password_hash="hash123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    payload = {
        "name": "Custom Owner Project",
        "description": "Created with explicit owner_id",
        "owner_id": user.id,
    }
    response = client.post("/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["owner_id"] == user.id
    assert data["name"] == "Custom Owner Project"


def test_create_project_nonexistent_owner(client):
    payload = {
        "name": "Invalid Project",
        "owner_id": 9999,
    }
    response = client.post("/projects", json=payload)
    assert response.status_code == 400
    assert "User with id 9999 does not exist" in response.json()["detail"]


def test_create_project_validation_error(client):
    # Empty name should fail validation
    payload = {"name": ""}
    response = client.post("/projects", json=payload)
    assert response.status_code == 422


def test_list_projects(client):
    client.post("/projects", json={"name": "Project Alpha"})
    client.post("/projects", json={"name": "Project Beta"})

    response = client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [p["name"] for p in data]
    assert "Project Alpha" in names
    assert "Project Beta" in names


def test_get_project_by_id(client):
    created = client.post("/projects", json={"name": "Project Gamma"}).json()
    project_id = created["id"]

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Project Gamma"


def test_get_project_not_found(client):
    response = client.get("/projects/99999")
    assert response.status_code == 404
    assert "Project with id 99999 not found" in response.json()["detail"]


def test_update_project(client):
    created = client.post("/projects", json={"name": "Original Name", "description": "Original Desc"}).json()
    project_id = created["id"]

    update_payload = {"name": "Updated Name", "description": "Updated Desc"}
    response = client.patch(f"/projects/{project_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated Desc"


def test_update_project_not_found(client):
    response = client.patch("/projects/99999", json={"name": "New Name"})
    assert response.status_code == 404


def test_delete_project(client):
    created = client.post("/projects", json={"name": "To Delete"}).json()
    project_id = created["id"]

    delete_res = client.delete(f"/projects/{project_id}")
    assert delete_res.status_code == 204

    get_res = client.get(f"/projects/{project_id}")
    assert get_res.status_code == 404


def test_delete_project_cascades_tasks(client):
    proj = client.post("/projects", json={"name": "Parent Project"}).json()
    project_id = proj["id"]

    task = client.post(
        "/tasks",
        json={"title": "Cascade Task", "project_id": project_id},
    ).json()
    task_id = task["id"]

    # Verify task exists
    assert client.get(f"/tasks/{task_id}").status_code == 200

    # Delete parent project
    assert client.delete(f"/projects/{project_id}").status_code == 204

    # Verify task was deleted by cascade
    assert client.get(f"/tasks/{task_id}").status_code == 404
