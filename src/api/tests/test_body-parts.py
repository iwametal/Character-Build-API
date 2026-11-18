"""Body parts API integration tests: /api/v1/body-parts."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_body_parts_crud(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/body-parts."""
    res = client.get("/api/v1/body-parts")
    assert res.status_code == 200
    assert len(res.json()) >= 5

    create_res = client.post(
        "/api/v1/body-parts",
        headers=member_headers,
        json={"body_part": "Wings"},
    )
    assert create_res.status_code == 201
    bpid = create_res.json()["id"]

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/body-parts/{bpid}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/body-parts/{bpid}", headers=admin_headers).status_code == 204
