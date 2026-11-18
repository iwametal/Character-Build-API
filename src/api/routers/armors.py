"""Armors router: /api/v1/armors."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import ArmorModel
from src.api.schemas import ArmorResponseSchema, ArmorSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/armors", tags=["Armor"])


@router.get("", response_model=list[ArmorResponseSchema])
def list_armors(db: Annotated[Session, Depends(get_db)]) -> list[ArmorModel]:
    """Retrieve all armors with body_part and rarity loaded."""
    stmt = select(ArmorModel).options(
        selectinload(ArmorModel.body_part),
        selectinload(ArmorModel.rarity),
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=ArmorResponseSchema, status_code=status.HTTP_201_CREATED)
def create_armor(
    payload: ArmorSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> ArmorModel:
    """Create a new armor equipment."""
    armor = ArmorModel(
        body_part_id=payload.body_part,
        atk=payload.atk,
        def_=payload.def_,
        hp=payload.hp,
        intelligence=payload.intelligence,
        vigor=payload.vigor,
        rarity_id=payload.rarity,
    )
    if payload.id is not None:
        armor.id = payload.id
    db.add(armor)
    db.commit()

    stmt = (
        select(ArmorModel)
        .where(ArmorModel.id == armor.id)
        .options(
            selectinload(ArmorModel.body_part),
            selectinload(ArmorModel.rarity),
        )
    )
    loaded = db.scalars(stmt).first()
    response.headers["Location"] = f"/api/v1/armors/{armor.id}"
    return loaded  # type: ignore[return-value]


@router.get("/{id}", response_model=ArmorResponseSchema)
def get_armor(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ArmorModel:
    """Retrieve an armor by ID."""
    stmt = (
        select(ArmorModel)
        .where(ArmorModel.id == id)
        .options(
            selectinload(ArmorModel.body_part),
            selectinload(ArmorModel.rarity),
        )
    )
    armor = db.scalars(stmt).first()
    if not armor:
        raise NotFoundException(f"Armor with id '{id}' not found.")
    return armor


@router.put("/{id}", response_model=ArmorResponseSchema)
def update_armor(
    id: int,
    payload: ArmorSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> ArmorModel:
    """Update an armor by ID."""
    armor = db.query(ArmorModel).filter(ArmorModel.id == id).first()
    if not armor:
        raise NotFoundException(f"Armor with id '{id}' not found.")
    armor.body_part_id = payload.body_part
    armor.atk = payload.atk
    armor.def_ = payload.def_
    armor.hp = payload.hp
    armor.intelligence = payload.intelligence
    armor.vigor = payload.vigor
    armor.rarity_id = payload.rarity
    db.commit()

    stmt = (
        select(ArmorModel)
        .where(ArmorModel.id == id)
        .options(
            selectinload(ArmorModel.body_part),
            selectinload(ArmorModel.rarity),
        )
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.patch("/{id}", response_model=ArmorResponseSchema)
def patch_armor(
    id: int,
    payload: ArmorSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> ArmorModel:
    """Partially update an armor by ID."""
    armor = db.query(ArmorModel).filter(ArmorModel.id == id).first()
    if not armor:
        raise NotFoundException(f"Armor with id '{id}' not found.")
    if payload.body_part is not None:
        armor.body_part_id = payload.body_part
    if payload.atk is not None:
        armor.atk = payload.atk
    if payload.def_ is not None:
        armor.def_ = payload.def_
    if payload.hp is not None:
        armor.hp = payload.hp
    if payload.intelligence is not None:
        armor.intelligence = payload.intelligence
    if payload.vigor is not None:
        armor.vigor = payload.vigor
    if payload.rarity is not None:
        armor.rarity_id = payload.rarity
    db.commit()

    stmt = (
        select(ArmorModel)
        .where(ArmorModel.id == id)
        .options(
            selectinload(ArmorModel.body_part),
            selectinload(ArmorModel.rarity),
        )
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_armor(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete an armor by ID (ADMIN only)."""
    armor = db.query(ArmorModel).filter(ArmorModel.id == id).first()
    if not armor:
        raise NotFoundException(f"Armor with id '{id}' not found.")
    db.delete(armor)
    db.commit()
