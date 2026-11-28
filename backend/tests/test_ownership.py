def test_user_cannot_access_other_users_project(client, auth_headers, other_auth_headers):
    # User A creates a project
    res_a = client.post(
        "/projects",
        json={"name": "User A Private Project", "description": "Confidential work"},
        headers=auth_headers,
    )
    assert res_a.status_code == 201
    project_id = res_a.json()["id"]

    # User B tries to view it -> 403 Forbidden
    res_b_get = client.get(f"/projects/{project_id}", headers=other_auth_headers)
    assert res_b_get.status_code == 403
    assert "permission" in res_b_get.json()["detail"].lower()

    # User B tries to update it -> 403 Forbidden
    res_b_patch = client.patch(
        f"/projects/{project_id}",
        json={"name": "Hacked Name"},
        headers=other_auth_headers,
    )
    assert res_b_patch.status_code == 403

    # User B tries to delete it -> 403 Forbidden
    res_b_delete = client.delete(f"/projects/{project_id}", headers=other_auth_headers)
    assert res_b_delete.status_code == 403

    # User B lists projects -> User A's project is NOT listed
    res_b_list = client.get("/projects", headers=other_auth_headers)
    assert res_b_list.status_code == 200
    listed_ids = [p["id"] for p in res_b_list.json()]
    assert project_id not in listed_ids


def test_user_cannot_add_task_to_other_users_project(client, auth_headers, other_auth_headers):
    # User A creates project
    res_a = client.post("/projects", json={"name": "User A Project"}, headers=auth_headers)
    project_id = res_a.json()["id"]

    # User B tries to create a task in User A's project -> 403 Forbidden
    res_b_task = client.post(
        "/tasks",
        json={"title": "Injected Task", "project_id": project_id},
        headers=other_auth_headers,
    )
    assert res_b_task.status_code == 403
    assert "permission" in res_b_task.json()["detail"].lower()


def test_user_cannot_access_or_modify_other_users_task(client, auth_headers, other_auth_headers):
    # User A creates project and task
    proj = client.post("/projects", json={"name": "User A Project"}, headers=auth_headers).json()
    task = client.post(
        "/tasks",
        json={"title": "User A Secret Task", "project_id": proj["id"]},
        headers=auth_headers,
    ).json()
    task_id = task["id"]

    # User B tries to get task -> 403 Forbidden
    assert client.get(f"/tasks/{task_id}", headers=other_auth_headers).status_code == 403

    # User B tries to update task -> 403 Forbidden
    assert client.patch(
        f"/tasks/{task_id}",
        json={"title": "Modified Title"},
        headers=other_auth_headers,
    ).status_code == 403

    # User B tries to delete task -> 403 Forbidden
    assert client.delete(f"/tasks/{task_id}", headers=other_auth_headers).status_code == 403

    # User B lists tasks -> User A's task is NOT listed
    res_b_list = client.get("/tasks", headers=other_auth_headers)
    assert res_b_list.status_code == 200
    listed_ids = [t["id"] for t in res_b_list.json()]
    assert task_id not in listed_ids


def test_user_cannot_suggest_subtasks_on_other_users_task(client, auth_headers, other_auth_headers):
    proj = client.post("/projects", json={"name": "User A Project"}, headers=auth_headers).json()
    task = client.post(
        "/tasks",
        json={"title": "User A Task", "project_id": proj["id"]},
        headers=auth_headers,
    ).json()

    # User B tries to call AI suggestions on User A's task -> 403 Forbidden
    res = client.post(f"/tasks/{task['id']}/suggest-subtasks", headers=other_auth_headers)
    assert res.status_code == 403
    assert "permission" in res.json()["detail"].lower()
