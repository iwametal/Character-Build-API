"""Jobs API integration tests: /api/v1/jobs."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_jobs_crud(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/jobs."""
    res = client.get("/api/v1/jobs")
    assert res.status_code == 200
    assert len(res.json()) >= 4

    create_res = client.post(
        "/api/v1/jobs",
        headers=member_headers,
        json={"job": "Necromancer", "atk": 10, "def": 5, "hp": 80, "vigor": 9, "intelligence": 20},
    )
    assert create_res.status_code == 201
    job = create_res.json()
    jid = job["id"]
    assert job["def"] == 5

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/jobs/{jid}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/jobs/{jid}", headers=admin_headers).status_code == 204
