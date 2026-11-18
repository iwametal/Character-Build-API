"""Authentication and authorization tests: /api/v1/auth."""

from __future__ import annotations

from datetime import timedelta
from fastapi.testclient import TestClient
from src.api.models import UserModel
from src.api.security import create_access_token


def test_login_admin_success(client: TestClient) -> None:
    """Valid admin credentials return 200 OK with token and user details."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fatec.sp.gov.br", "password": "Admin@2026"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"
    assert data["expiresIn"] == 3600
    assert data["user"]["email"] == "admin@fatec.sp.gov.br"
    assert data["user"]["role"] == "ADMIN"


def test_login_member_success(client: TestClient) -> None:
    """Valid member credentials return 200 OK with token and MEMBER role."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "aluno@fatec.sp.gov.br", "password": "Aluno@2026"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert data["user"]["role"] == "MEMBER"


def test_login_invalid_password(client: TestClient) -> None:
    """Wrong password returns 401 Unauthorized in RFC 9457 format."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fatec.sp.gov.br", "password": "WrongPassword123"},
    )
    assert response.status_code == 401
    error = response.json()
    assert error["type"] == "https://api.character-build.dev/errors/unauthorized"
    assert error["status"] == 401
    assert "invalid" in error["detail"].lower()


def test_login_user_not_found(client: TestClient) -> None:
    """Unregistered email returns 401 Unauthorized in RFC 9457 format."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@fatec.sp.gov.br", "password": "Admin@2026"},
    )
    assert response.status_code == 401
    error = response.json()
    assert error["type"] == "https://api.character-build.dev/errors/unauthorized"


def test_get_me_authenticated(client: TestClient, admin_headers: dict[str, str]) -> None:
    """GET /api/v1/auth/me with Bearer token returns current user profile."""
    response = client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@fatec.sp.gov.br"
    assert data["role"] == "ADMIN"


def test_get_me_missing_token(client: TestClient) -> None:
    """GET /api/v1/auth/me without token returns 401 Unauthorized (RFC 9457)."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    error = response.json()
    assert error["type"] == "https://api.character-build.dev/errors/unauthorized"
    assert error["status"] == 401


def test_get_me_invalid_token(client: TestClient) -> None:
    """GET /api/v1/auth/me with invalid token returns 401 Unauthorized."""
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.xyz"})
    assert response.status_code == 401
    error = response.json()
    assert error["type"] == "https://api.character-build.dev/errors/unauthorized"


def test_get_me_expired_token(client: TestClient, admin_user: UserModel) -> None:
    """GET /api/v1/auth/me with expired token returns 401 Unauthorized."""
    expired_token = create_access_token(
        sub=admin_user.id,
        email=admin_user.email,
        role="ADMIN",
        expires_delta=timedelta(seconds=-10),
    )
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    error = response.json()
    assert error["type"] == "https://api.character-build.dev/errors/unauthorized"
    assert "expired" in error["detail"].lower()
