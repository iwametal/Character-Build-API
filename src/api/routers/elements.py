"""Elements router: /api/v1/elements."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import ElementModel
from src.api.schemas import ElementSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/elements", tags=["Elements"])


@router.get("", response_model=list[ElementSchema])
def list_elements(db: Annotated[Session, Depends(get_db)]) -> list[ElementModel]:
    """Retrieve all elements with relationships loaded via selectinload."""
    stmt = select(ElementModel).options(
        selectinload(ElementModel.strength_rel),
        selectinload(ElementModel.weakness_rel),
    )
    return list(db.scalars(stmt).all())


@router.post("", response_model=ElementSchema, status_code=status.HTTP_201_CREATED)
def create_element(
    payload: ElementSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> ElementModel:
    """Create a new element."""
    elem = ElementModel(
        element=payload.element,
        strength_id=payload.strength,
        weakness_id=payload.weakness,
    )
    if payload.id is not None:
        elem.id = payload.id
    db.add(elem)
    db.commit()
    db.refresh(elem)
    response.headers["Location"] = f"/api/v1/elements/{elem.id}"
    return elem


@router.get("/{id}", response_model=ElementSchema)
def get_element(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ElementModel:
    """Retrieve an element by ID."""
    stmt = (
        select(ElementModel)
        .where(ElementModel.id == id)
        .options(
            selectinload(ElementModel.strength_rel),
            selectinload(ElementModel.weakness_rel),
        )
    )
    elem = db.scalars(stmt).first()
    if not elem:
        raise NotFoundException(f"Element with id '{id}' not found.")
    return elem


@router.put("/{id}", response_model=ElementSchema)
def update_element(
    id: int,
    payload: ElementSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> ElementModel:
    """Update an element by ID."""
    elem = db.query(ElementModel).filter(ElementModel.id == id).first()
    if not elem:
        raise NotFoundException(f"Element with id '{id}' not found.")
    elem.element = payload.element
    elem.strength_id = payload.strength
    elem.weakness_id = payload.weakness
    db.commit()
    db.refresh(elem)
    return elem


@router.patch("/{id}", response_model=ElementSchema)
def patch_element(
    id: int,
    payload: ElementSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> ElementModel:
    """Partially update an element by ID."""
    elem = db.query(ElementModel).filter(ElementModel.id == id).first()
    if not elem:
        raise NotFoundException(f"Element with id '{id}' not found.")
    if payload.element:
        elem.element = payload.element
    if payload.strength is not None:
        elem.strength_id = payload.strength
    if payload.weakness is not None:
        elem.weakness_id = payload.weakness
    db.commit()
    db.refresh(elem)
    return elem


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_element(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete an element by ID (ADMIN only)."""
    elem = db.query(ElementModel).filter(ElementModel.id == id).first()
    if not elem:
        raise NotFoundException(f"Element with id '{id}' not found.")
    db.delete(elem)
    db.commit()
