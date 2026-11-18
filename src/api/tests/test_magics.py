"""Magics API integration tests: /api/v1/magics."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_magics_crud(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """Test full CRUD on /api/v1/magics with element and status relations."""
    # List has seeded magic
    res = client.get("/api/v1/magics")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Create new magic
    create_res = client.post(
        "/api/v1/magics",
        headers=member_headers,
        json={
            "magic": "Ice Blizzard",
            "damage": 50,
            "element": 2,  # Água
            "lv_required": 5,
            "mana_consumption": 20,
            "shield": 10,
            "status": 2,   # Congelamento
        },
    )
    assert create_res.status_code == 201
    magic = create_res.json()
    magic_id = magic["id"]
    assert magic["element"]["element"] == "Água"
    assert magic["status"]["status"] == "Congelamento"

    # Member DELETE -> 403
    assert client.delete(f"/api/v1/magics/{magic_id}", headers=member_headers).status_code == 403

    # Admin DELETE -> 204
    assert client.delete(f"/api/v1/magics/{magic_id}", headers=admin_headers).status_code == 204
