from unittest.mock import MagicMock, patch
from app.core.config import settings
from app.schemas.ai import SubtaskItem, SubtaskSuggestionResponse


def test_suggest_subtasks_unauthenticated(client):
    res = client.post("/tasks/1/suggest-subtasks")
    assert res.status_code == 401


def test_suggest_subtasks_nonexistent_task(client, auth_headers):
    res = client.post("/tasks/99999/suggest-subtasks", headers=auth_headers)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_suggest_subtasks_missing_api_key(client, auth_headers):
    proj = client.post("/projects", json={"name": "P"}, headers=auth_headers).json()
    task = client.post("/tasks", json={"title": "T", "project_id": proj["id"]}, headers=auth_headers).json()

    # Ensure GEMINI_API_KEY is unset
    original_key = settings.GEMINI_API_KEY
    try:
        settings.GEMINI_API_KEY = None
        res = client.post(f"/tasks/{task['id']}/suggest-subtasks", headers=auth_headers)
        assert res.status_code == 503
        assert "GEMINI_API_KEY" in res.json()["detail"]
    finally:
        settings.GEMINI_API_KEY = original_key


def test_suggest_subtasks_mock_success_and_no_autopersist(client, auth_headers):
    proj = client.post("/projects", json={"name": "P"}, headers=auth_headers).json()
    task = client.post("/tasks", json={"title": "Design Database", "project_id": proj["id"]}, headers=auth_headers).json()
    task_id = task["id"]

    mock_response = SubtaskSuggestionResponse(
        task_id=task_id,
        task_title="Design Database",
        subtasks=[
            SubtaskItem(title="Draft ER Diagram", description="Sketch table relationships"),
            SubtaskItem(title="Write Alembic Migration", description="Generate migration script"),
        ],
    )

    with patch("app.api.tasks.generate_subtask_suggestions", return_value=mock_response):
        res = client.post(f"/tasks/{task_id}/suggest-subtasks", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["task_id"] == task_id
        assert len(data["subtasks"]) == 2
        assert data["subtasks"][0]["title"] == "Draft ER Diagram"
        assert data["subtasks"][1]["title"] == "Write Alembic Migration"

    # CRITICAL CHECK: Verify suggestions were NOT auto-saved to DB!
    tasks_res = client.get(f"/tasks?project_id={proj['id']}", headers=auth_headers)
    assert tasks_res.status_code == 200
    # Should still only have the 1 original task
    assert len(tasks_res.json()) == 1
    assert tasks_res.json()[0]["id"] == task_id


def test_suggest_subtasks_malformed_ai_output_handling(client, auth_headers):
    proj = client.post("/projects", json={"name": "P"}, headers=auth_headers).json()
    task = client.post("/tasks", json={"title": "T", "project_id": proj["id"]}, headers=auth_headers).json()

    original_key = settings.GEMINI_API_KEY
    try:
        settings.GEMINI_API_KEY = "test_fake_key"
        with patch("google.genai.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_response = MagicMock()
            # Malformed JSON returned by model
            mock_response.text = "NOT_VALID_JSON"
            mock_client.models.generate_content.return_value = mock_response
            mock_client_cls.return_value = mock_client

            res = client.post(f"/tasks/{task['id']}/suggest-subtasks", headers=auth_headers)
            assert res.status_code == 502
            assert "json" in res.json()["detail"].lower()
    finally:
        settings.GEMINI_API_KEY = original_key


def test_batch_create_tasks_approval(client, auth_headers, other_auth_headers):
    proj = client.post("/projects", json={"name": "Approval Project"}, headers=auth_headers).json()
    project_id = proj["id"]

    batch_payload = {
        "project_id": project_id,
        "tasks": [
            {"title": "Subtask 1", "description": "First approved item"},
            {"title": "Subtask 2", "description": "Second approved item"},
        ],
    }

    # Batch save as User A (owner) -> 201 Created
    res = client.post("/tasks/batch", json=batch_payload, headers=auth_headers)
    assert res.status_code == 201
    created_tasks = res.json()
    assert len(created_tasks) == 2
    assert created_tasks[0]["title"] == "Subtask 1"
    assert created_tasks[1]["title"] == "Subtask 2"

    # User B tries to batch-save to User A's project -> 403 Forbidden
    res_b = client.post("/tasks/batch", json=batch_payload, headers=other_auth_headers)
    assert res_b.status_code == 403
