"""Rarities API integration tests: /api/v1/rarities."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_rarities_crud(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/rarities."""
    res = client.get("/api/v1/rarities")
    assert res.status_code == 200
    assert len(res.json()) >= 5

    create_res = client.post(
        "/api/v1/rarities",
        headers=member_headers,
        json={"rarity": "Mythic"},
    )
    assert create_res.status_code == 201
    rid = create_res.json()["id"]

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/rarities/{rid}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/rarities/{rid}", headers=admin_headers).status_code == 204
