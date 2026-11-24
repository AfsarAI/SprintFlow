from datetime import timedelta
from app.core.security import create_access_token


def test_projects_unauthenticated(client):
    # No auth header -> 401
    assert client.get("/projects").status_code == 401
    assert client.post("/projects", json={"name": "P"}).status_code == 401
    assert client.get("/projects/1").status_code == 401
    assert client.patch("/projects/1", json={"name": "P2"}).status_code == 401
    assert client.delete("/projects/1").status_code == 401


def test_projects_invalid_or_expired_token(client, test_user):
    # Invalid token
    res = client.get("/projects", headers={"Authorization": "Bearer invalid"})
    assert res.status_code == 401

    # Expired token
    expired_token = create_access_token(subject=test_user.id, expires_delta=timedelta(seconds=-5))
    res = client.get("/projects", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401


def test_create_project_authenticated(client, auth_headers, test_user):
    payload = {
        "name": "SprintFlow MVP",
        "description": "Initial SprintFlow development project",
    }
    response = client.post("/projects", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "SprintFlow MVP"
    assert data["description"] == "Initial SprintFlow development project"
    assert "id" in data
    assert data["owner_id"] == test_user.id
    assert "created_at" in data
    assert "updated_at" in data


def test_create_project_validation_error(client, auth_headers):
    # Empty name should fail validation
    payload = {"name": ""}
    response = client.post("/projects", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_list_projects(client, auth_headers):
    client.post("/projects", json={"name": "Project Alpha"}, headers=auth_headers)
    client.post("/projects", json={"name": "Project Beta"}, headers=auth_headers)

    response = client.get("/projects", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [p["name"] for p in data]
    assert "Project Alpha" in names
    assert "Project Beta" in names


def test_get_project_by_id(client, auth_headers):
    created = client.post("/projects", json={"name": "Project Gamma"}, headers=auth_headers).json()
    project_id = created["id"]

    response = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Project Gamma"


def test_get_project_not_found(client, auth_headers):
    response = client.get("/projects/99999", headers=auth_headers)
    assert response.status_code == 404
    assert "Project with id 99999 not found" in response.json()["detail"]


def test_update_project(client, auth_headers):
    created = client.post("/projects", json={"name": "Original Name", "description": "Original Desc"}, headers=auth_headers).json()
    project_id = created["id"]

    update_payload = {"name": "Updated Name", "description": "Updated Desc"}
    response = client.patch(f"/projects/{project_id}", json=update_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated Desc"


def test_update_project_not_found(client, auth_headers):
    response = client.patch("/projects/99999", json={"name": "New Name"}, headers=auth_headers)
    assert response.status_code == 404


def test_delete_project(client, auth_headers):
    created = client.post("/projects", json={"name": "To Delete"}, headers=auth_headers).json()
    project_id = created["id"]

    delete_res = client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert delete_res.status_code == 204

    get_res = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert get_res.status_code == 404


def test_delete_project_cascades_tasks(client, auth_headers):
    proj = client.post("/projects", json={"name": "Parent Project"}, headers=auth_headers).json()
    project_id = proj["id"]

    task = client.post(
        "/tasks",
        json={"title": "Cascade Task", "project_id": project_id},
        headers=auth_headers,
    ).json()
    task_id = task["id"]

    # Verify task exists
    assert client.get(f"/tasks/{task_id}", headers=auth_headers).status_code == 200

    # Delete parent project
    assert client.delete(f"/projects/{project_id}", headers=auth_headers).status_code == 204

    # Verify task was deleted by cascade
    assert client.get(f"/tasks/{task_id}", headers=auth_headers).status_code == 404
