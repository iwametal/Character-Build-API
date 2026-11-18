"""Tasks API integration tests: /api/v1/tasks."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_tasks_public(client: TestClient) -> None:
    """GET /api/v1/tasks is public."""
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_task_unauthenticated(client: TestClient) -> None:
    """POST /api/v1/tasks without token returns 401 Unauthorized."""
    response = client.post("/api/v1/tasks", json={"title": "Draft Quest"})
    assert response.status_code == 401
    assert response.json()["type"] == "https://api.character-build.dev/errors/unauthorized"


def test_create_task_invalid_project_id_404(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """POST /api/v1/tasks with non-existent projectId returns 404 (SPEC.md §4.3)."""
    response = client.post(
        "/api/v1/tasks",
        headers=member_headers,
        json={"title": "Find Item", "projectId": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404
    assert response.json()["type"] == "https://api.character-build.dev/errors/not-found"


def test_create_task_success(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """POST /api/v1/tasks creates task and returns 201 with Location header."""
    response = client.post(
        "/api/v1/tasks",
        headers=member_headers,
        json={"title": "Explore dungeon", "status": "IN_PROGRESS", "priority": "HIGH"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Explore dungeon"
    assert data["status"] == "IN_PROGRESS"
    assert response.headers.get("Location") == f"/api/v1/tasks/{data['id']}"


def test_delete_task_rbac_member_forbidden(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """MEMBER trying DELETE /api/v1/tasks/{id} receives 403 Forbidden (RFC 9457)."""
    create_res = client.post(
        "/api/v1/tasks",
        headers=member_headers,
        json={"title": "Task to delete"},
    )
    task_id = create_res.json()["id"]

    response = client.delete(f"/api/v1/tasks/{task_id}", headers=member_headers)
    assert response.status_code == 403
    assert response.json()["type"] == "https://api.character-build.dev/errors/forbidden"


def test_delete_task_rbac_admin_success(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """ADMIN deleting task receives 204 No Content."""
    create_res = client.post(
        "/api/v1/tasks",
        headers=member_headers,
        json={"title": "Task to delete"},
    )
    task_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/tasks/{task_id}", headers=admin_headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/tasks/{task_id}")
    assert get_res.status_code == 404
