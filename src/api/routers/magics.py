"""Magics router: /api/v1/magics."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import MagicModel
from src.api.schemas import MagicAbilityResponseSchema, MagicAbilitySchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/magics", tags=["Magic"])


@router.get("", response_model=list[MagicAbilityResponseSchema])
def list_magics(db: Annotated[Session, Depends(get_db)]) -> list[MagicModel]:
    """Retrieve all magic skills with element and status effect loaded."""
    stmt = select(MagicModel).options(
        selectinload(MagicModel.element),
        selectinload(MagicModel.status),
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=MagicAbilityResponseSchema, status_code=status.HTTP_201_CREATED)
def create_magic(
    payload: MagicAbilitySchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> MagicModel:
    """Create a new magic skill."""
    magic = MagicModel(
        magic=payload.magic,
        damage=payload.damage,
        element_id=payload.element,
        lv_required=payload.lv_required,
        mana_consumption=payload.mana_consumption,
        shield=payload.shield,
        status_id=payload.status,
    )
    if payload.id is not None:
        magic.id = payload.id
    db.add(magic)
    db.commit()

    stmt = (
        select(MagicModel)
        .where(MagicModel.id == magic.id)
        .options(
            selectinload(MagicModel.element),
            selectinload(MagicModel.status),
        )
    )
    loaded = db.scalars(stmt).first()
    response.headers["Location"] = f"/api/v1/magics/{magic.id}"
    return loaded  # type: ignore[return-value]


@router.get("/{id}", response_model=MagicAbilityResponseSchema)
def get_magic(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> MagicModel:
    """Retrieve a magic skill by ID."""
    stmt = (
        select(MagicModel)
        .where(MagicModel.id == id)
        .options(
            selectinload(MagicModel.element),
            selectinload(MagicModel.status),
        )
    )
    magic = db.scalars(stmt).first()
    if not magic:
        raise NotFoundException(f"Magic with id '{id}' not found.")
    return magic


@router.put("/{id}", response_model=MagicAbilityResponseSchema)
def update_magic(
    id: int,
    payload: MagicAbilitySchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> MagicModel:
    """Update a magic skill by ID."""
    magic = db.query(MagicModel).filter(MagicModel.id == id).first()
    if not magic:
        raise NotFoundException(f"Magic with id '{id}' not found.")
    magic.magic = payload.magic
    magic.damage = payload.damage
    magic.element_id = payload.element
    magic.lv_required = payload.lv_required
    magic.mana_consumption = payload.mana_consumption
    magic.shield = payload.shield
    magic.status_id = payload.status
    db.commit()

    stmt = (
        select(MagicModel)
        .where(MagicModel.id == id)
        .options(
            selectinload(MagicModel.element),
            selectinload(MagicModel.status),
        )
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.patch("/{id}", response_model=MagicAbilityResponseSchema)
def patch_magic(
    id: int,
    payload: MagicAbilitySchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> MagicModel:
    """Partially update a magic skill by ID."""
    magic = db.query(MagicModel).filter(MagicModel.id == id).first()
    if not magic:
        raise NotFoundException(f"Magic with id '{id}' not found.")
    if payload.magic:
        magic.magic = payload.magic
    if payload.damage is not None:
        magic.damage = payload.damage
    if payload.element is not None:
        magic.element_id = payload.element
    if payload.lv_required is not None:
        magic.lv_required = payload.lv_required
    if payload.mana_consumption is not None:
        magic.mana_consumption = payload.mana_consumption
    if payload.shield is not None:
        magic.shield = payload.shield
    if payload.status is not None:
        magic.status_id = payload.status
    db.commit()

    stmt = (
        select(MagicModel)
        .where(MagicModel.id == id)
        .options(
            selectinload(MagicModel.element),
            selectinload(MagicModel.status),
        )
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_magic(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a magic skill by ID (ADMIN only)."""
    magic = db.query(MagicModel).filter(MagicModel.id == id).first()
    if not magic:
        raise NotFoundException(f"Magic with id '{id}' not found.")
    db.delete(magic)
    db.commit()
