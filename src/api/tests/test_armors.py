"""Armors API integration tests: /api/v1/armors."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_and_create_armor(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/armors with nested body_part and rarity."""
    # List is public
    res = client.get("/api/v1/armors")
    assert res.status_code == 200

    # Create armor with body_part 1 and rarity 3
    create_res = client.post(
        "/api/v1/armors",
        headers=member_headers,
        json={
            "body_part": 1,
            "atk": 5,
            "def": 30,
            "hp": 100,
            "intelligence": 10,
            "vigor": 15,
            "rarity": 3,
        },
    )
    assert create_res.status_code == 201
    armor = create_res.json()
    armor_id = armor["id"]
    assert armor["body_part"]["id"] == 1
    assert armor["rarity"]["id"] == 3
    assert armor["def"] == 30

    # Get by ID
    get_res = client.get(f"/api/v1/armors/{armor_id}")
    assert get_res.status_code == 200

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/armors/{armor_id}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/armors/{armor_id}", headers=admin_headers).status_code == 204
