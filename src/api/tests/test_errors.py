"""RFC 9457 (Problem Details for HTTP APIs) compliance tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_error_401_format_rfc9457(client: TestClient) -> None:
    """Missing token on protected endpoint returns RFC 9457 formatted 401."""
    response = client.post("/api/v1/characters", json={})
    assert response.status_code == 401
    err = response.json()
    assert err["type"] == "https://api.character-build.dev/errors/unauthorized"
    assert err["title"] == "Unauthorized"
    assert err["status"] == 401
    assert "detail" in err
    assert "instance" in err
    assert err["instance"] == "/api/v1/characters"


def test_error_403_format_rfc9457(client: TestClient, member_headers: dict[str, str]) -> None:
    """MEMBER attempting DELETE returns RFC 9457 formatted 403 Forbidden."""
    response = client.delete("/api/v1/characters/any-id", headers=member_headers)
    assert response.status_code == 403
    err = response.json()
    assert err["type"] == "https://api.character-build.dev/errors/forbidden"
    assert err["title"] == "Forbidden"
    assert err["status"] == 403
    assert "detail" in err
    assert err["instance"] == "/api/v1/characters/any-id"


def test_error_404_format_rfc9457(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Non-existent resource returns RFC 9457 formatted 404 Not Found."""
    response = client.get("/api/v1/characters/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    err = response.json()
    assert err["type"] == "https://api.character-build.dev/errors/not-found"
    assert err["title"] == "Not Found"
    assert err["status"] == 404
    assert "detail" in err


def test_error_422_format_rfc9457_with_invalid_params(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """Invalid payload triggers 422 with invalidParams list in RFC 9457 format."""
    response = client.post(
        "/api/v1/characters",
        headers=member_headers,
        json={"name": "Arthur"},  # Missing required fields like last_name, age, etc.
    )
    assert response.status_code == 422
    err = response.json()
    assert err["type"] == "https://api.character-build.dev/errors/validation-error"
    assert err["title"] == "Unprocessable Entity"
    assert err["status"] == 422
    assert "invalidParams" in err
    assert isinstance(err["invalidParams"], list)
    assert len(err["invalidParams"]) > 0
    param = err["invalidParams"][0]
    assert "name" in param
    assert "reason" in param


def test_no_default_fastapi_detail_format(
    client: TestClient, member_headers: dict[str, str]
) -> None:
    """Ensure error is never returned as FastAPI's default {'detail': '...'} or {'detail': [...]}."""
    response = client.post(
        "/api/v1/characters",
        headers=member_headers,
        json={},
    )
    data = response.json()
    # If detail is present, it must be a string explanation, not a list of raw validation errors
    if "detail" in data:
        assert isinstance(data["detail"], str)
    # The RFC 9457 required fields must be present
    assert "type" in data
    assert "title" in data
    assert "status" in data
    assert "instance" in data
