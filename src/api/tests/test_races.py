"""Races API integration tests: /api/v1/races."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_races_crud(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/races."""
    res = client.get("/api/v1/races")
    assert res.status_code == 200
    assert len(res.json()) >= 4

    create_res = client.post(
        "/api/v1/races",
        headers=member_headers,
        json={"race": "Dragonborn", "atk": 18, "def": 15, "hp": 150, "intelligence": 12, "mana": 40, "vigor": 16},
    )
    assert create_res.status_code == 201
    race = create_res.json()
    rid = race["id"]
    assert race["def"] == 15

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/races/{rid}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/races/{rid}", headers=admin_headers).status_code == 204
