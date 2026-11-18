"""Authentication router: /api/v1/auth."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.exceptions import UnauthorizedException
from src.api.models import UserModel
from src.api.schemas import LoginRequestDTO, TokenResponseDTO, UserResponse
from src.api.security import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    create_access_token,
    get_current_user,
    user_to_response,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponseDTO)
def login(
    payload: LoginRequestDTO,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponseDTO:
    """Authenticate with email/username and password, returning a JWT token."""
    identifier = payload.email or payload.username
    if not identifier:
        raise UnauthorizedException("Email or username must be provided.")

    user = (
        db.query(UserModel)
        .filter((UserModel.email == identifier) | (UserModel.name == identifier))
        .first()
    )

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedException("Invalid email or password.")

    token = create_access_token(sub=user.id, email=user.email, role=user.role)

    return TokenResponseDTO(
        accessToken=token,
        tokenType="bearer",
        expiresIn=ACCESS_TOKEN_EXPIRE_SECONDS,
        user=user_to_response(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return user_to_response(current_user)
