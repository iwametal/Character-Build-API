"""Status effects API integration tests: /api/v1/status-effects."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_status_effects_crud(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/status-effects."""
    res = client.get("/api/v1/status-effects")
    assert res.status_code == 200
    assert len(res.json()) >= 4

    create_res = client.post(
        "/api/v1/status-effects",
        headers=member_headers,
        json={"status": "Petrify", "duration": 3},
    )
    assert create_res.status_code == 201
    seid = create_res.json()["id"]

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/status-effects/{seid}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/status-effects/{seid}", headers=admin_headers).status_code == 204
