"""Races router: /api/v1/races."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import RaceModel
from src.api.schemas import RaceResponseSchema, RaceSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/races", tags=["Race"])


@router.get("", response_model=list[RaceResponseSchema])
def list_races(db: Annotated[Session, Depends(get_db)]) -> list[RaceModel]:
    """Retrieve all races."""
    return db.query(RaceModel).all()


@router.post("", response_model=RaceResponseSchema, status_code=status.HTTP_201_CREATED)
def create_race(
    payload: RaceSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> RaceModel:
    """Create a new race."""
    race = RaceModel(
        race=payload.race,
        atk=payload.atk,
        def_=payload.def_,
        hp=payload.hp,
        intelligence=payload.intelligence,
        mana=payload.mana,
        vigor=payload.vigor,
    )
    if payload.id is not None:
        race.id = payload.id
    db.add(race)
    db.commit()
    db.refresh(race)
    response.headers["Location"] = f"/api/v1/races/{race.id}"
    return race


@router.get("/{id}", response_model=RaceResponseSchema)
def get_race(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> RaceModel:
    """Retrieve a race by ID."""
    race = db.query(RaceModel).filter(RaceModel.id == id).first()
    if not race:
        raise NotFoundException(f"Race with id '{id}' not found.")
    return race


@router.put("/{id}", response_model=RaceResponseSchema)
def update_race(
    id: int,
    payload: RaceSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> RaceModel:
    """Update a race by ID."""
    race = db.query(RaceModel).filter(RaceModel.id == id).first()
    if not race:
        raise NotFoundException(f"Race with id '{id}' not found.")
    race.race = payload.race
    race.atk = payload.atk
    race.def_ = payload.def_
    race.hp = payload.hp
    race.intelligence = payload.intelligence
    race.mana = payload.mana
    race.vigor = payload.vigor
    db.commit()
    db.refresh(race)
    return race


@router.patch("/{id}", response_model=RaceResponseSchema)
def patch_race(
    id: int,
    payload: RaceSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> RaceModel:
    """Partially update a race by ID."""
    race = db.query(RaceModel).filter(RaceModel.id == id).first()
    if not race:
        raise NotFoundException(f"Race with id '{id}' not found.")
    fields = payload.model_dump(exclude_unset=True, by_alias=False)
    for field, value in fields.items():
        if field == "id" or value is None:
            continue
        setattr(race, field, value)
    db.commit()
    db.refresh(race)
    return race


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_race(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a race by ID (ADMIN only)."""
    race = db.query(RaceModel).filter(RaceModel.id == id).first()
    if not race:
        raise NotFoundException(f"Race with id '{id}' not found.")
    db.delete(race)
    db.commit()
