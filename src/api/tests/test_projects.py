"""Projects API integration tests: /api/v1/projects."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_projects_public(client: TestClient) -> None:
    """GET /api/v1/projects is public."""
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_project_and_embed_tasks(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """POST /api/v1/projects, associate tasks, and fetch embedded tasks (1:N ORM)."""
    # 1. Create project
    proj_res = client.post(
        "/api/v1/projects",
        headers=member_headers,
        json={"name": "Campaign Alpha", "description": "Epic saga"},
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 2. Add tasks linked to project
    t1 = client.post(
        "/api/v1/tasks",
        headers=member_headers,
        json={"title": "Prologue", "projectId": proj_id},
    )
    assert t1.status_code == 201

    t2 = client.post(
        "/api/v1/tasks",
        headers=member_headers,
        json={"title": "Act I", "projectId": proj_id},
    )
    assert t2.status_code == 201

    # 3. GET /api/v1/projects/{id} - tasks preloaded
    get_proj = client.get(f"/api/v1/projects/{proj_id}")
    assert get_proj.status_code == 200
    assert len(get_proj.json()["tasks"]) == 2

    # 4. GET /api/v1/projects/{projectId}/tasks (SPEC.md §4.3)
    tasks_res = client.get(f"/api/v1/projects/{proj_id}/tasks")
    assert tasks_res.status_code == 200
    data = tasks_res.json()
    assert "data" in data
    assert len(data["data"]) == 2


def test_get_project_tasks_not_found(client: TestClient) -> None:
    """GET /api/v1/projects/{projectId}/tasks on non-existent project returns 404."""
    response = client.get("/api/v1/projects/00000000-0000-0000-0000-000000000000/tasks")
    assert response.status_code == 404
    assert response.json()["type"] == "https://api.character-build.dev/errors/not-found"


def test_delete_project_rbac(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """MEMBER gets 403 on DELETE project, ADMIN gets 204."""
    proj_res = client.post(
        "/api/v1/projects",
        headers=member_headers,
        json={"name": "Temp Project"},
    )
    proj_id = proj_res.json()["id"]

    # Member fails
    res_member = client.delete(f"/api/v1/projects/{proj_id}", headers=member_headers)
    assert res_member.status_code == 403

    # Admin succeeds
    res_admin = client.delete(f"/api/v1/projects/{proj_id}", headers=admin_headers)
    assert res_admin.status_code == 204
