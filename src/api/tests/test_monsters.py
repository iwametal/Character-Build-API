"""Monsters API integration tests: /api/v1/monsters."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_monster_crud_and_rbac(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/monsters with race relation."""
    # List is public
    res = client.get("/api/v1/monsters")
    assert res.status_code == 200

    # Create monster
    create_res = client.post(
        "/api/v1/monsters",
        headers=member_headers,
        json={
            "name": "Red Dragon",
            "race": 1,
            "atk": 200,
            "def": 150,
            "hp": 2000,
            "intelligence": 80,
            "vigor": 120,
        },
    )
    assert create_res.status_code == 201
    monster = create_res.json()
    monster_id = monster["id"]
    assert monster["name"] == "Red Dragon"
    assert monster["race"]["race"] == "Humano"

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/monsters/{monster_id}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/monsters/{monster_id}", headers=admin_headers).status_code == 204
