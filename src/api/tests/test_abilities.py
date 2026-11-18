"""Abilities API integration tests: /api/v1/abilities."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_abilities(client: TestClient) -> None:
    """GET /api/v1/abilities is public."""
    response = client.get("/api/v1/abilities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_and_delete_ability(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Create ability linked to character and magic, test RBAC on DELETE."""
    # 1. Create character
    char_res = client.post(
        "/api/v1/characters",
        headers=member_headers,
        json={
            "name": "Mage",
            "lastName": "Merlin",
            "age": 100,
            "level": 50,
            "gender": 1,
            "job": 2,
            "race": 1,
        },
    )
    char_id = char_res.json()["id"]

    # 2. Create ability linking character to seeded magic #1
    abl_res = client.post(
        "/api/v1/abilities",
        headers=member_headers,
        json={"character": char_id, "magic": 1},
    )
    assert abl_res.status_code == 201
    abl_id = abl_res.json()["id"]
    assert abl_res.json()["character"]["name"] == "Mage"
    assert abl_res.json()["magic"]["magic"] == "Bola de Fogo"

    # 3. Member tries to delete ability -> 403
    del_member = client.delete(f"/api/v1/abilities/{abl_id}", headers=member_headers)
    assert del_member.status_code == 403

    # 4. Admin deletes ability -> 204
    del_admin = client.delete(f"/api/v1/abilities/{abl_id}", headers=admin_headers)
    assert del_admin.status_code == 204
