"""Body parts router: /api/v1/body-parts."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import BodyPartModel
from src.api.schemas import BodyPartSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/body-parts", tags=["Body-Parts"])


@router.get("", response_model=list[BodyPartSchema])
def list_body_parts(db: Annotated[Session, Depends(get_db)]) -> list[BodyPartModel]:
    """Retrieve all body parts."""
    return db.query(BodyPartModel).all()


@router.post("", response_model=BodyPartSchema, status_code=status.HTTP_201_CREATED)
def create_body_part(
    payload: BodyPartSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> BodyPartModel:
    """Create a new body part."""
    body_part = BodyPartModel(body_part=payload.body_part)
    if payload.id is not None:
        body_part.id = payload.id
    db.add(body_part)
    db.commit()
    db.refresh(body_part)
    response.headers["Location"] = f"/api/v1/body-parts/{body_part.id}"
    return body_part


@router.get("/{id}", response_model=BodyPartSchema)
def get_body_part(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> BodyPartModel:
    """Retrieve a body part by ID."""
    body_part = db.query(BodyPartModel).filter(BodyPartModel.id == id).first()
    if not body_part:
        raise NotFoundException(f"Body part with id '{id}' not found.")
    return body_part


@router.put("/{id}", response_model=BodyPartSchema)
def update_body_part(
    id: int,
    payload: BodyPartSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> BodyPartModel:
    """Update a body part by ID."""
    body_part = db.query(BodyPartModel).filter(BodyPartModel.id == id).first()
    if not body_part:
        raise NotFoundException(f"Body part with id '{id}' not found.")
    body_part.body_part = payload.body_part
    db.commit()
    db.refresh(body_part)
    return body_part


@router.patch("/{id}", response_model=BodyPartSchema)
def patch_body_part(
    id: int,
    payload: BodyPartSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> BodyPartModel:
    """Partially update a body part by ID."""
    body_part = db.query(BodyPartModel).filter(BodyPartModel.id == id).first()
    if not body_part:
        raise NotFoundException(f"Body part with id '{id}' not found.")
    if payload.body_part:
        body_part.body_part = payload.body_part
    db.commit()
    db.refresh(body_part)
    return body_part


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_body_part(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a body part by ID (ADMIN only)."""
    body_part = db.query(BodyPartModel).filter(BodyPartModel.id == id).first()
    if not body_part:
        raise NotFoundException(f"Body part with id '{id}' not found.")
    db.delete(body_part)
    db.commit()
