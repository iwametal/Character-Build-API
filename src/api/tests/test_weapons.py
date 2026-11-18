"""Weapons API integration tests: /api/v1/weapons."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_and_create_weapon(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/weapons with magic relation."""
    res = client.get("/api/v1/weapons")
    assert res.status_code == 200

    create_res = client.post(
        "/api/v1/weapons",
        headers=member_headers,
        json={
            "name": "Excalibur",
            "atk": 150,
            "def": 20,
            "hp": 50,
            "intelligence": 30,
            "vigor": 25,
            "magic": 1,
        },
    )
    assert create_res.status_code == 201
    weapon = create_res.json()
    weapon_id = weapon["id"]
    assert weapon["name"] == "Excalibur"
    assert weapon["magic"]["magic"] == "Bola de Fogo"

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/weapons/{weapon_id}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/weapons/{weapon_id}", headers=admin_headers).status_code == 204
