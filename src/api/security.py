"""JWT generation/validation and FastAPI RBAC dependency factories.

Implements STYLEGUIDE.md §3.3:
  - HS256 tokens with claims: sub, email, role, iat, exp
  - 401 Unauthorized (RFC 9457) for missing/invalid/expired tokens
  - 403 Forbidden  (RFC 9457) for authenticated users lacking the required role
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.exceptions import ForbiddenException, UnauthorizedException
from src.api.models import UserModel
from src.api.schemas import UserResponse

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SECRET_KEY: str = os.getenv(
    "SECRET_KEY",
    "change-me-to-a-secure-random-secret-of-at-least-32-bytes!",
)
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600  # 1 hour per SPEC.md §4.1

_bearer_scheme = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the stored *hashed* password."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def get_password_hash(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


# ---------------------------------------------------------------------------
# Token generation
# ---------------------------------------------------------------------------


def create_access_token(
    sub: str,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Sign and return a JWT with the required SPEC.md claims.

    Claims: sub, email, role, iat, exp.
    Algorithm: HS256.
    """
    now = datetime.now(UTC)
    expire = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    )
    payload: dict = {
        "sub": sub,
        "email": email,
        "role": role,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# Token decoding helper
# ---------------------------------------------------------------------------


def _decode_token(token: str) -> dict:
    """Decode and validate a JWT; raise UnauthorizedException on any failure."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Token is invalid or malformed.")


# ---------------------------------------------------------------------------
# FastAPI dependency: get_current_user
# ---------------------------------------------------------------------------


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> UserModel:
    """Require a valid Bearer token; return the authenticated UserModel.

    Raises UnauthorizedException (401 RFC 9457) when:
      - Authorization header is absent
      - Token is malformed or expired
      - User no longer exists in the database
    """
    if credentials is None or not credentials.credentials:
        raise UnauthorizedException(
            "Authorization header is missing. "
            "Provide a Bearer token to access this resource."
        )

    payload = _decode_token(credentials.credentials)

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token payload is missing the 'sub' claim.")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise UnauthorizedException("Authenticated user no longer exists.")

    return user


# ---------------------------------------------------------------------------
# FastAPI dependency: get_optional_current_user
# ---------------------------------------------------------------------------


def get_optional_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> UserModel | None:
    """Return the authenticated UserModel if a valid token is supplied,
    or None when no Authorization header is present.

    Used for public GET routes where authentication is optional (SPEC.md §4.2).
    """
    if credentials is None or not credentials.credentials:
        return None

    payload = _decode_token(credentials.credentials)
    user_id: str | None = payload.get("sub")
    if not user_id:
        return None

    return db.query(UserModel).filter(UserModel.id == user_id).first()


# ---------------------------------------------------------------------------
# FastAPI dependency factory: require_role
# ---------------------------------------------------------------------------


def require_role(*allowed_roles: str):
    """Return a FastAPI dependency that enforces role-based access control.

    Usage:
        @router.delete("/{id}", dependencies=[Depends(require_role("ADMIN"))])

    Raises:
        UnauthorizedException (401) — when no valid token is provided.
        ForbiddenException    (403) — when the authenticated user's role is
                                      not in *allowed_roles*.
    """

    def _dependency(
        user: Annotated[UserModel, Depends(get_current_user)],
    ) -> UserModel:
        if user.role not in allowed_roles:
            raise ForbiddenException(
                f"This action requires one of the following roles: "
                f"{', '.join(allowed_roles)}. "
                f"Your current role is '{user.role}'."
            )
        return user

    return _dependency


# ---------------------------------------------------------------------------
# Convenience: serialize UserModel → UserResponse
# ---------------------------------------------------------------------------


def user_to_response(user: UserModel) -> UserResponse:
    """Convert a UserModel ORM instance to a UserResponse Pydantic schema."""
    return UserResponse.model_validate(user)
