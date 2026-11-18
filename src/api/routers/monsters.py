"""Monsters router: /api/v1/monsters."""

from __future__ import annotations

import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import MonsterModel, RaceModel
from src.api.schemas import MonsterResponseSchema, MonsterSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/monsters", tags=["Monster"])


def _resolve_race_id(race_input: str | int | None, db: Session) -> int | None:
    if race_input is None:
        return None
    if isinstance(race_input, int):
        return race_input
    if isinstance(race_input, str):
        if race_input.isdigit():
            return int(race_input)
        race_obj = db.query(RaceModel).filter(RaceModel.race == race_input).first()
        if race_obj:
            return race_obj.id
    return None


@router.get("", response_model=list[MonsterResponseSchema])
def list_monsters(db: Annotated[Session, Depends(get_db)]) -> list[MonsterModel]:
    """Retrieve all monsters with race loaded."""
    stmt = select(MonsterModel).options(
        selectinload(MonsterModel.race),
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=MonsterResponseSchema, status_code=status.HTTP_201_CREATED)
def create_monster(
    payload: MonsterSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> MonsterModel:
    """Create a new monster."""
    monster_id = payload.id or str(uuid.uuid4())
    race_id = _resolve_race_id(payload.race, db)

    monster = MonsterModel(
        id=monster_id,
        name=payload.name,
        race_id=race_id,
        atk=payload.atk,
        def_=payload.def_,
        hp=payload.hp,
        intelligence=payload.intelligence,
        vigor=payload.vigor,
    )
    db.add(monster)
    db.commit()

    stmt = (
        select(MonsterModel)
        .where(MonsterModel.id == monster.id)
        .options(
            selectinload(MonsterModel.race),
        )
    )
    loaded = db.scalars(stmt).first()
    response.headers["Location"] = f"/api/v1/monsters/{monster.id}"
    return loaded  # type: ignore[return-value]


@router.get("/{id}", response_model=MonsterResponseSchema)
def get_monster(
    id: str,
    db: Annotated[Session, Depends(get_db)],
) -> MonsterModel:
    """Retrieve a monster by UUID."""
    stmt = (
        select(MonsterModel)
        .where(MonsterModel.id == id)
        .options(
            selectinload(MonsterModel.race),
        )
    )
    monster = db.scalars(stmt).first()
    if not monster:
        raise NotFoundException(f"Monster with id '{id}' not found.")
    return monster


@router.put("/{id}", response_model=MonsterResponseSchema)
def update_monster(
    id: str,
    payload: MonsterSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> MonsterModel:
    """Update a monster by UUID."""
    monster = db.query(MonsterModel).filter(MonsterModel.id == id).first()
    if not monster:
        raise NotFoundException(f"Monster with id '{id}' not found.")
    monster.name = payload.name
    monster.race_id = _resolve_race_id(payload.race, db)
    monster.atk = payload.atk
    monster.def_ = payload.def_
    monster.hp = payload.hp
    monster.intelligence = payload.intelligence
    monster.vigor = payload.vigor
    db.commit()

    stmt = (
        select(MonsterModel)
        .where(MonsterModel.id == id)
        .options(
            selectinload(MonsterModel.race),
        )
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.patch("/{id}", response_model=MonsterResponseSchema)
def patch_monster(
    id: str,
    payload: MonsterSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> MonsterModel:
    """Partially update a monster by UUID."""
    monster = db.query(MonsterModel).filter(MonsterModel.id == id).first()
    if not monster:
        raise NotFoundException(f"Monster with id '{id}' not found.")
    if payload.name:
        monster.name = payload.name
    if payload.race is not None:
        monster.race_id = _resolve_race_id(payload.race, db)
    if payload.atk is not None:
        monster.atk = payload.atk
    if payload.def_ is not None:
        monster.def_ = payload.def_
    if payload.hp is not None:
        monster.hp = payload.hp
    if payload.intelligence is not None:
        monster.intelligence = payload.intelligence
    if payload.vigor is not None:
        monster.vigor = payload.vigor
    db.commit()

    stmt = (
        select(MonsterModel)
        .where(MonsterModel.id == id)
        .options(
            selectinload(MonsterModel.race),
        )
    )
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monster(
    id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a monster by UUID (ADMIN only)."""
    monster = db.query(MonsterModel).filter(MonsterModel.id == id).first()
    if not monster:
        raise NotFoundException(f"Monster with id '{id}' not found.")
    db.delete(monster)
    db.commit()
