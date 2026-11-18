"""Genders API integration tests: /api/v1/genders."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_genders_crud(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/genders."""
    res = client.get("/api/v1/genders")
    assert res.status_code == 200
    assert len(res.json()) >= 3

    create_res = client.post(
        "/api/v1/genders",
        headers=member_headers,
        json={"gender": "CustomGender"},
    )
    assert create_res.status_code == 201
    gid = create_res.json()["id"]

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/genders/{gid}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/genders/{gid}", headers=admin_headers).status_code == 204
