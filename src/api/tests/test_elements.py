"""Elements API integration tests: /api/v1/elements."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_elements_crud(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/elements."""
    res = client.get("/api/v1/elements")
    assert res.status_code == 200
    assert len(res.json()) >= 4

    create_res = client.post(
        "/api/v1/elements",
        headers=member_headers,
        json={"element": "Lightning", "strength": 2, "weakness": 3},
    )
    assert create_res.status_code == 201
    elem_id = create_res.json()["id"]

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/elements/{elem_id}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/elements/{elem_id}", headers=admin_headers).status_code == 204
