"""Rarities router: /api/v1/rarities."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import RarityModel
from src.api.schemas import RaritySchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/rarities", tags=["Rarities"])


@router.get("", response_model=list[RaritySchema])
def list_rarities(db: Annotated[Session, Depends(get_db)]) -> list[RarityModel]:
    """Retrieve all rarities."""
    return db.query(RarityModel).all()


@router.post("", response_model=RaritySchema, status_code=status.HTTP_201_CREATED)
def create_rarity(
    payload: RaritySchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> RarityModel:
    """Create a new rarity."""
    rarity = RarityModel(rarity=payload.rarity)
    if payload.id is not None:
        rarity.id = payload.id
    db.add(rarity)
    db.commit()
    db.refresh(rarity)
    response.headers["Location"] = f"/api/v1/rarities/{rarity.id}"
    return rarity


@router.get("/{id}", response_model=RaritySchema)
def get_rarity(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> RarityModel:
    """Retrieve a rarity by ID."""
    rarity = db.query(RarityModel).filter(RarityModel.id == id).first()
    if not rarity:
        raise NotFoundException(f"Rarity with id '{id}' not found.")
    return rarity


@router.put("/{id}", response_model=RaritySchema)
def update_rarity(
    id: int,
    payload: RaritySchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> RarityModel:
    """Update a rarity by ID."""
    rarity = db.query(RarityModel).filter(RarityModel.id == id).first()
    if not rarity:
        raise NotFoundException(f"Rarity with id '{id}' not found.")
    rarity.rarity = payload.rarity
    db.commit()
    db.refresh(rarity)
    return rarity


@router.patch("/{id}", response_model=RaritySchema)
def patch_rarity(
    id: int,
    payload: RaritySchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> RarityModel:
    """Partially update a rarity by ID."""
    rarity = db.query(RarityModel).filter(RarityModel.id == id).first()
    if not rarity:
        raise NotFoundException(f"Rarity with id '{id}' not found.")
    if payload.rarity:
        rarity.rarity = payload.rarity
    db.commit()
    db.refresh(rarity)
    return rarity


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rarity(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a rarity by ID (ADMIN only)."""
    rarity = db.query(RarityModel).filter(RarityModel.id == id).first()
    if not rarity:
        raise NotFoundException(f"Rarity with id '{id}' not found.")
    db.delete(rarity)
    db.commit()
