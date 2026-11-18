"""Abilities router: /api/v1/abilities."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import (
    AbilityModel,
    CharacterModel,
    MagicModel,
    PhysicalAbilityModel,
)
from src.api.schemas import AbilityResponseSchema, AbilitySchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/abilities", tags=["Ability"])


def _ability_selectin_options():
    return (
        selectinload(AbilityModel.character).selectinload(CharacterModel.gender),
        selectinload(AbilityModel.character).selectinload(CharacterModel.job),
        selectinload(AbilityModel.character).selectinload(CharacterModel.race),
        selectinload(AbilityModel.magic).selectinload(MagicModel.element),
        selectinload(AbilityModel.magic).selectinload(MagicModel.status),
        selectinload(AbilityModel.physical).selectinload(PhysicalAbilityModel.status),
    )


@router.get("", response_model=list[AbilityResponseSchema])
def list_abilities(db: Annotated[Session, Depends(get_db)]) -> list[AbilityModel]:
    """Retrieve all abilities with character, magic, and physical abilities loaded."""
    stmt = select(AbilityModel).options(*_ability_selectin_options())
    return list(db.scalars(stmt).all())


@router.post("", response_model=AbilityResponseSchema, status_code=status.HTTP_201_CREATED)
def create_ability(
    payload: AbilitySchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> AbilityModel:
    """Create a new ability association."""
    char_id = str(payload.character) if payload.character else None
    if char_id:
        char = db.query(CharacterModel).filter(CharacterModel.id == char_id).first()
        if not char:
            raise NotFoundException(f"Character with id '{char_id}' not found.")

    if payload.magic:
        magic = db.query(MagicModel).filter(MagicModel.id == payload.magic).first()
        if not magic:
            raise NotFoundException(f"Magic with id '{payload.magic}' not found.")

    if payload.physical:
        phys = (
            db.query(PhysicalAbilityModel)
            .filter(PhysicalAbilityModel.id == payload.physical)
            .first()
        )
        if not phys:
            raise NotFoundException(f"Physical ability with id '{payload.physical}' not found.")

    ability = AbilityModel(
        character_id=char_id,  # type: ignore[arg-type]
        magic_id=payload.magic,
        physical_id=payload.physical,
    )
    if payload.id is not None:
        ability.id = payload.id
    db.add(ability)
    db.commit()

    stmt = (
        select(AbilityModel)
        .where(AbilityModel.id == ability.id)
        .options(*_ability_selectin_options())
    )
    loaded = db.scalars(stmt).first()
    response.headers["Location"] = f"/api/v1/abilities/{ability.id}"
    return loaded  # type: ignore[return-value]


@router.get("/{id}", response_model=AbilityResponseSchema)
def get_ability(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> AbilityModel:
    """Retrieve an ability by ID."""
    stmt = (
        select(AbilityModel)
        .where(AbilityModel.id == id)
        .options(*_ability_selectin_options())
    )
    ability = db.scalars(stmt).first()
    if not ability:
        raise NotFoundException(f"Ability with id '{id}' not found.")
    return ability


@router.put("/{id}", response_model=AbilityResponseSchema)
def update_ability(
    id: int,
    payload: AbilitySchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> AbilityModel:
    """Update an ability by ID."""
    ability = db.query(AbilityModel).filter(AbilityModel.id == id).first()
    if not ability:
        raise NotFoundException(f"Ability with id '{id}' not found.")

    if payload.character:
        char_id = str(payload.character)
        char = db.query(CharacterModel).filter(CharacterModel.id == char_id).first()
        if not char:
            raise NotFoundException(f"Character with id '{char_id}' not found.")
        ability.character_id = char_id

    ability.magic_id = payload.magic
    ability.physical_id = payload.physical
    db.commit()

    stmt = (
        select(AbilityModel)
        .where(AbilityModel.id == id)
        .options(*_ability_selectin_options())
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.patch("/{id}", response_model=AbilityResponseSchema)
def patch_ability(
    id: int,
    payload: AbilitySchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> AbilityModel:
    """Partially update an ability by ID."""
    ability = db.query(AbilityModel).filter(AbilityModel.id == id).first()
    if not ability:
        raise NotFoundException(f"Ability with id '{id}' not found.")

    if payload.character is not None:
        char_id = str(payload.character)
        char = db.query(CharacterModel).filter(CharacterModel.id == char_id).first()
        if not char:
            raise NotFoundException(f"Character with id '{char_id}' not found.")
        ability.character_id = char_id

    if payload.magic is not None:
        ability.magic_id = payload.magic
    if payload.physical is not None:
        ability.physical_id = payload.physical

    db.commit()

    stmt = (
        select(AbilityModel)
        .where(AbilityModel.id == id)
        .options(*_ability_selectin_options())
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ability(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete an ability by ID (ADMIN only)."""
    ability = db.query(AbilityModel).filter(AbilityModel.id == id).first()
    if not ability:
        raise NotFoundException(f"Ability with id '{id}' not found.")
    db.delete(ability)
    db.commit()
