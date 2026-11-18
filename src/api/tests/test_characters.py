"""Characters API integration tests: /api/v1/characters."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _sample_character_payload() -> dict:
    return {
        "name": "Artoria",
        "lastName": "Pendragon",
        "age": 25,
        "level": 10,
        "extraMana": 50,
        "gender": 2,  # Feminino
        "job": 1,     # Guerreiro
        "race": 1,    # Humano
    }


def test_list_characters_public(client: TestClient) -> None:
    """GET /api/v1/characters is publicly accessible without token."""
    response = client.get("/api/v1/characters")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_character_unauthorized(client: TestClient) -> None:
    """POST /api/v1/characters without token returns 401 Unauthorized."""
    response = client.post("/api/v1/characters", json=_sample_character_payload())
    assert response.status_code == 401
    assert response.json()["type"] == "https://api.character-build.dev/errors/unauthorized"


def test_create_character_invalid_foreign_key(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """POST /api/v1/characters with invalid FK returns 404 Not Found."""
    payload = _sample_character_payload()
    payload["gender"] = 999  # Inexistent gender
    response = client.post("/api/v1/characters", headers=member_headers, json=payload)
    assert response.status_code == 404
    assert response.json()["type"] == "https://api.character-build.dev/errors/not-found"


def test_create_character_success(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """POST /api/v1/characters creates character and populates nested relations."""
    payload = _sample_character_payload()
    response = client.post("/api/v1/characters", headers=member_headers, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Artoria"
    assert data["last_name"] == "Pendragon"
    assert data["gender"]["gender"] == "Feminino"
    assert data["job"]["job"] == "Guerreiro"
    assert data["race"]["race"] == "Humano"
    assert response.headers.get("Location") == f"/api/v1/characters/{data['id']}"


def test_get_character_by_id(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """GET /api/v1/characters/{id} returns character with nested data."""
    create_res = client.post(
        "/api/v1/characters", headers=member_headers, json=_sample_character_payload()
    )
    char_id = create_res.json()["id"]

    response = client.get(f"/api/v1/characters/{char_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == char_id
    assert data["name"] == "Artoria"


def test_update_character_put(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """PUT /api/v1/characters/{id} updates character entirely."""
    create_res = client.post(
        "/api/v1/characters", headers=member_headers, json=_sample_character_payload()
    )
    char_id = create_res.json()["id"]

    updated_payload = _sample_character_payload()
    updated_payload["name"] = "Artoria Alter"
    updated_payload["level"] = 50

    response = client.put(
        f"/api/v1/characters/{char_id}", headers=member_headers, json=updated_payload
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Artoria Alter"
    assert response.json()["level"] == 50


def test_patch_character(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """PATCH /api/v1/characters/{id} updates character partially."""
    create_res = client.post(
        "/api/v1/characters", headers=member_headers, json=_sample_character_payload()
    )
    char_id = create_res.json()["id"]

    response = client.patch(
        f"/api/v1/characters/{char_id}",
        headers=member_headers,
        json={"name": "Saber", "lastName": "King", "level": 90, "age": 25, "gender": 2, "job": 1, "race": 1},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Saber"
    assert response.json()["level"] == 90


def test_delete_character_rbac_member_forbidden(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """MEMBER attempting DELETE on character gets 403 Forbidden (RFC 9457)."""
    create_res = client.post(
        "/api/v1/characters", headers=member_headers, json=_sample_character_payload()
    )
    char_id = create_res.json()["id"]

    response = client.delete(f"/api/v1/characters/{char_id}", headers=member_headers)
    assert response.status_code == 403
    assert response.json()["type"] == "https://api.character-build.dev/errors/forbidden"


def test_delete_character_rbac_admin_success(
    client: TestClient, member_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    """ADMIN deleting character receives 204 No Content, subsequent GET returns 404."""
    create_res = client.post(
        "/api/v1/characters", headers=member_headers, json=_sample_character_payload()
    )
    char_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/characters/{char_id}", headers=admin_headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/characters/{char_id}")
    assert get_res.status_code == 404
