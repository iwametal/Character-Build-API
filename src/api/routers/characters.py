"""Characters router: /api/v1/characters."""

from __future__ import annotations

import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import CharacterModel, GenderModel, JobModel, RaceModel
from src.api.schemas import CharacterResponseSchema, CharacterSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/characters", tags=["Character"])


def _validate_foreign_keys(gender_id: int, job_id: int, race_id: int, db: Session) -> None:
    if not db.query(GenderModel).filter(GenderModel.id == gender_id).first():
        raise NotFoundException(f"Gender with id '{gender_id}' not found.")
    if not db.query(JobModel).filter(JobModel.id == job_id).first():
        raise NotFoundException(f"Job with id '{job_id}' not found.")
    if not db.query(RaceModel).filter(RaceModel.id == race_id).first():
        raise NotFoundException(f"Race with id '{race_id}' not found.")


@router.get("", response_model=list[CharacterResponseSchema])
def list_characters(db: Annotated[Session, Depends(get_db)]) -> list[CharacterModel]:
    """Retrieve all characters with gender, job, and race loaded via selectinload."""
    stmt = select(CharacterModel).options(
        selectinload(CharacterModel.gender),
        selectinload(CharacterModel.job),
        selectinload(CharacterModel.race),
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=CharacterResponseSchema, status_code=status.HTTP_201_CREATED)
def create_character(
    payload: CharacterSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> CharacterModel:
    """Create a new character with foreign key validation."""
    _validate_foreign_keys(payload.gender, payload.job, payload.race, db)

    char_id = payload.id or str(uuid.uuid4())
    character = CharacterModel(
        id=char_id,
        name=payload.name,
        last_name=payload.last_name,
        age=payload.age,
        level=payload.level,
        extra_mana=payload.extra_mana,
        gender_id=payload.gender,
        job_id=payload.job,
        race_id=payload.race,
    )
    db.add(character)
    db.commit()

    stmt = (
        select(CharacterModel)
        .where(CharacterModel.id == character.id)
        .options(
            selectinload(CharacterModel.gender),
            selectinload(CharacterModel.job),
            selectinload(CharacterModel.race),
        )
    )
    loaded = db.scalars(stmt).first()
    response.headers["Location"] = f"/api/v1/characters/{character.id}"
    return loaded  # type: ignore[return-value]


@router.get("/{id}", response_model=CharacterResponseSchema)
def get_character(
    id: str,
    db: Annotated[Session, Depends(get_db)],
) -> CharacterModel:
    """Retrieve a character by UUID with relationships loaded."""
    stmt = (
        select(CharacterModel)
        .where(CharacterModel.id == id)
        .options(
            selectinload(CharacterModel.gender),
            selectinload(CharacterModel.job),
            selectinload(CharacterModel.race),
        )
    )
    character = db.scalars(stmt).first()
    if not character:
        raise NotFoundException(f"Character with id '{id}' not found.")
    return character


@router.put("/{id}", response_model=CharacterResponseSchema)
def update_character(
    id: str,
    payload: CharacterSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> CharacterModel:
    """Update a character by UUID."""
    character = db.query(CharacterModel).filter(CharacterModel.id == id).first()
    if not character:
        raise NotFoundException(f"Character with id '{id}' not found.")

    _validate_foreign_keys(payload.gender, payload.job, payload.race, db)

    character.name = payload.name
    character.last_name = payload.last_name
    character.age = payload.age
    character.level = payload.level
    character.extra_mana = payload.extra_mana
    character.gender_id = payload.gender
    character.job_id = payload.job
    character.race_id = payload.race
    db.commit()

    stmt = (
        select(CharacterModel)
        .where(CharacterModel.id == id)
        .options(
            selectinload(CharacterModel.gender),
            selectinload(CharacterModel.job),
            selectinload(CharacterModel.race),
        )
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.patch("/{id}", response_model=CharacterResponseSchema)
def patch_character(
    id: str,
    payload: CharacterSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> CharacterModel:
    """Partially update a character by UUID."""
    character = db.query(CharacterModel).filter(CharacterModel.id == id).first()
    if not character:
        raise NotFoundException(f"Character with id '{id}' not found.")

    if payload.name:
        character.name = payload.name
    if payload.last_name:
        character.last_name = payload.last_name
    if payload.age:
        character.age = payload.age
    if payload.level:
        character.level = payload.level
    if payload.extra_mana is not None:
        character.extra_mana = payload.extra_mana
    if payload.gender:
        if not db.query(GenderModel).filter(GenderModel.id == payload.gender).first():
            raise NotFoundException(f"Gender with id '{payload.gender}' not found.")
        character.gender_id = payload.gender
    if payload.job:
        if not db.query(JobModel).filter(JobModel.id == payload.job).first():
            raise NotFoundException(f"Job with id '{payload.job}' not found.")
        character.job_id = payload.job
    if payload.race:
        if not db.query(RaceModel).filter(RaceModel.id == payload.race).first():
            raise NotFoundException(f"Race with id '{payload.race}' not found.")
        character.race_id = payload.race
    db.commit()

    stmt = (
        select(CharacterModel)
        .where(CharacterModel.id == id)
        .options(
            selectinload(CharacterModel.gender),
            selectinload(CharacterModel.job),
            selectinload(CharacterModel.race),
        )
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(
    id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a character by UUID (ADMIN only)."""
    character = db.query(CharacterModel).filter(CharacterModel.id == id).first()
    if not character:
        raise NotFoundException(f"Character with id '{id}' not found.")
    db.delete(character)
    db.commit()
