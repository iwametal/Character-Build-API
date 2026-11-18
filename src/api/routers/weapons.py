"""Weapons router: /api/v1/weapons."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import WeaponModel
from src.api.schemas import WeaponResponseSchema, WeaponSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/weapons", tags=["Weapon"])


@router.get("", response_model=list[WeaponResponseSchema])
def list_weapons(db: Annotated[Session, Depends(get_db)]) -> list[WeaponModel]:
    """Retrieve all weapons with magic ability loaded."""
    stmt = select(WeaponModel).options(
        selectinload(WeaponModel.magic),
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=WeaponResponseSchema, status_code=status.HTTP_201_CREATED)
def create_weapon(
    payload: WeaponSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> WeaponModel:
    """Create a new weapon equipment."""
    weapon = WeaponModel(
        name=payload.name,
        atk=payload.atk,
        def_=payload.def_,
        hp=payload.hp,
        intelligence=payload.intelligence,
        vigor=payload.vigor,
        magic_id=payload.magic,
    )
    if payload.id is not None:
        weapon.id = payload.id
    db.add(weapon)
    db.commit()

    stmt = (
        select(WeaponModel)
        .where(WeaponModel.id == weapon.id)
        .options(
            selectinload(WeaponModel.magic),
        )
    )
    loaded = db.scalars(stmt).first()
    response.headers["Location"] = f"/api/v1/weapons/{weapon.id}"
    return loaded  # type: ignore[return-value]


@router.get("/{id}", response_model=WeaponResponseSchema)
def get_weapon(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> WeaponModel:
    """Retrieve a weapon by ID."""
    stmt = (
        select(WeaponModel)
        .where(WeaponModel.id == id)
        .options(
            selectinload(WeaponModel.magic),
        )
    )
    weapon = db.scalars(stmt).first()
    if not weapon:
        raise NotFoundException(f"Weapon with id '{id}' not found.")
    return weapon


@router.put("/{id}", response_model=WeaponResponseSchema)
def update_weapon(
    id: int,
    payload: WeaponSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> WeaponModel:
    """Update a weapon by ID."""
    weapon = db.query(WeaponModel).filter(WeaponModel.id == id).first()
    if not weapon:
        raise NotFoundException(f"Weapon with id '{id}' not found.")
    weapon.name = payload.name
    weapon.atk = payload.atk
    weapon.def_ = payload.def_
    weapon.hp = payload.hp
    weapon.intelligence = payload.intelligence
    weapon.vigor = payload.vigor
    weapon.magic_id = payload.magic
    db.commit()

    stmt = (
        select(WeaponModel)
        .where(WeaponModel.id == id)
        .options(
            selectinload(WeaponModel.magic),
        )
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.patch("/{id}", response_model=WeaponResponseSchema)
def patch_weapon(
    id: int,
    payload: WeaponSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> WeaponModel:
    """Partially update a weapon by ID."""
    weapon = db.query(WeaponModel).filter(WeaponModel.id == id).first()
    if not weapon:
        raise NotFoundException(f"Weapon with id '{id}' not found.")
    if payload.name:
        weapon.name = payload.name
    if payload.atk is not None:
        weapon.atk = payload.atk
    if payload.def_ is not None:
        weapon.def_ = payload.def_
    if payload.hp is not None:
        weapon.hp = payload.hp
    if payload.intelligence is not None:
        weapon.intelligence = payload.intelligence
    if payload.vigor is not None:
        weapon.vigor = payload.vigor
    if payload.magic is not None:
        weapon.magic_id = payload.magic
    db.commit()

    stmt = (
        select(WeaponModel)
        .where(WeaponModel.id == id)
        .options(
            selectinload(WeaponModel.magic),
        )
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_weapon(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a weapon by ID (ADMIN only)."""
    weapon = db.query(WeaponModel).filter(WeaponModel.id == id).first()
    if not weapon:
        raise NotFoundException(f"Weapon with id '{id}' not found.")
    db.delete(weapon)
    db.commit()
