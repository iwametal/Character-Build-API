"""Status effects router: /api/v1/status-effects."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import StatusEffectModel
from src.api.schemas import StatusEffectSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/status-effects", tags=["Status-Effects"])


@router.get("", response_model=list[StatusEffectSchema])
def list_status_effects(db: Annotated[Session, Depends(get_db)]) -> list[StatusEffectModel]:
    """Retrieve all status effects."""
    return db.query(StatusEffectModel).all()


@router.post("", response_model=StatusEffectSchema, status_code=status.HTTP_201_CREATED)
def create_status_effect(
    payload: StatusEffectSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> StatusEffectModel:
    """Create a new status effect."""
    effect = StatusEffectModel(status=payload.status, duration=payload.duration)
    if payload.id is not None:
        effect.id = payload.id
    db.add(effect)
    db.commit()
    db.refresh(effect)
    response.headers["Location"] = f"/api/v1/status-effects/{effect.id}"
    return effect


@router.get("/{id}", response_model=StatusEffectSchema)
def get_status_effect(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> StatusEffectModel:
    """Retrieve a status effect by ID."""
    effect = db.query(StatusEffectModel).filter(StatusEffectModel.id == id).first()
    if not effect:
        raise NotFoundException(f"Status effect with id '{id}' not found.")
    return effect


@router.put("/{id}", response_model=StatusEffectSchema)
def update_status_effect(
    id: int,
    payload: StatusEffectSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> StatusEffectModel:
    """Update a status effect by ID."""
    effect = db.query(StatusEffectModel).filter(StatusEffectModel.id == id).first()
    if not effect:
        raise NotFoundException(f"Status effect with id '{id}' not found.")
    effect.status = payload.status
    effect.duration = payload.duration
    db.commit()
    db.refresh(effect)
    return effect


@router.patch("/{id}", response_model=StatusEffectSchema)
def patch_status_effect(
    id: int,
    payload: StatusEffectSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> StatusEffectModel:
    """Partially update a status effect by ID."""
    effect = db.query(StatusEffectModel).filter(StatusEffectModel.id == id).first()
    if not effect:
        raise NotFoundException(f"Status effect with id '{id}' not found.")
    if payload.status:
        effect.status = payload.status
    if payload.duration is not None:
        effect.duration = payload.duration
    db.commit()
    db.refresh(effect)
    return effect


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status_effect(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a status effect by ID (ADMIN only)."""
    effect = db.query(StatusEffectModel).filter(StatusEffectModel.id == id).first()
    if not effect:
        raise NotFoundException(f"Status effect with id '{id}' not found.")
    db.delete(effect)
    db.commit()
