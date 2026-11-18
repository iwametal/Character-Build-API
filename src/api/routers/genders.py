"""Genders router: /api/v1/genders."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import GenderModel
from src.api.schemas import GenderSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/genders", tags=["Genders"])


@router.get("", response_model=list[GenderSchema])
def list_genders(db: Annotated[Session, Depends(get_db)]) -> list[GenderModel]:
    """Retrieve all genders."""
    return db.query(GenderModel).all()


@router.post("", response_model=GenderSchema, status_code=status.HTTP_201_CREATED)
def create_gender(
    payload: GenderSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> GenderModel:
    """Create a new gender."""
    gender = GenderModel(gender=payload.gender)
    if payload.id is not None:
        gender.id = payload.id
    db.add(gender)
    db.commit()
    db.refresh(gender)
    response.headers["Location"] = f"/api/v1/genders/{gender.id}"
    return gender


@router.get("/{id}", response_model=GenderSchema)
def get_gender(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> GenderModel:
    """Retrieve a gender by ID."""
    gender = db.query(GenderModel).filter(GenderModel.id == id).first()
    if not gender:
        raise NotFoundException(f"Gender with id '{id}' not found.")
    return gender


@router.put("/{id}", response_model=GenderSchema)
def update_gender(
    id: int,
    payload: GenderSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> GenderModel:
    """Update a gender by ID."""
    gender = db.query(GenderModel).filter(GenderModel.id == id).first()
    if not gender:
        raise NotFoundException(f"Gender with id '{id}' not found.")
    gender.gender = payload.gender
    db.commit()
    db.refresh(gender)
    return gender


@router.patch("/{id}", response_model=GenderSchema)
def patch_gender(
    id: int,
    payload: GenderSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> GenderModel:
    """Partially update a gender by ID."""
    gender = db.query(GenderModel).filter(GenderModel.id == id).first()
    if not gender:
        raise NotFoundException(f"Gender with id '{id}' not found.")
    if payload.gender:
        gender.gender = payload.gender
    db.commit()
    db.refresh(gender)
    return gender


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gender(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a gender by ID (ADMIN only)."""
    gender = db.query(GenderModel).filter(GenderModel.id == id).first()
    if not gender:
        raise NotFoundException(f"Gender with id '{id}' not found.")
    db.delete(gender)
    db.commit()
