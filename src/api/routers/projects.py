"""Projects router: /api/v1/projects."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import ProjectModel
from src.api.schemas import ProjectResponseSchema, ProjectSchema, TaskResponseSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponseSchema])
def list_projects(db: Annotated[Session, Depends(get_db)]) -> list[ProjectModel]:
    """Retrieve all projects with preloaded tasks to avoid N+1 queries."""
    stmt = select(ProjectModel).options(selectinload(ProjectModel.tasks))
    return list(db.scalars(stmt).all())


@router.post("", response_model=ProjectResponseSchema, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> ProjectModel:
    """Create a new project."""
    project_id = payload.id or str(uuid.uuid4())
    project = ProjectModel(
        id=project_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(project)
    db.commit()

    stmt = select(ProjectModel).where(ProjectModel.id == project.id).options(selectinload(ProjectModel.tasks))
    loaded = db.scalars(stmt).first()
    response.headers["Location"] = f"/api/v1/projects/{project.id}"
    return loaded  # type: ignore[return-value]


@router.get("/{id}", response_model=ProjectResponseSchema)
def get_project(
    id: str,
    db: Annotated[Session, Depends(get_db)],
) -> ProjectModel:
    """Retrieve a project by ID with its embedded tasks."""
    stmt = select(ProjectModel).where(ProjectModel.id == id).options(selectinload(ProjectModel.tasks))
    project = db.scalars(stmt).first()
    if not project:
        raise NotFoundException(f"Project with id '{id}' not found.")
    return project


@router.put("/{id}", response_model=ProjectResponseSchema)
def update_project(
    id: str,
    payload: ProjectSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> ProjectModel:
    """Update a project."""
    project = db.query(ProjectModel).filter(ProjectModel.id == id).first()
    if not project:
        raise NotFoundException(f"Project with id '{id}' not found.")
    project.name = payload.name
    project.description = payload.description
    project.updated_at = datetime.utcnow()
    db.commit()

    stmt = select(ProjectModel).where(ProjectModel.id == id).options(selectinload(ProjectModel.tasks))
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.patch("/{id}", response_model=ProjectResponseSchema)
def patch_project(
    id: str,
    payload: ProjectSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> ProjectModel:
    """Partially update a project."""
    project = db.query(ProjectModel).filter(ProjectModel.id == id).first()
    if not project:
        raise NotFoundException(f"Project with id '{id}' not found.")
    if payload.name:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    project.updated_at = datetime.utcnow()
    db.commit()

    stmt = select(ProjectModel).where(ProjectModel.id == id).options(selectinload(ProjectModel.tasks))
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a project (ADMIN only)."""
    project = db.query(ProjectModel).filter(ProjectModel.id == id).first()
    if not project:
        raise NotFoundException(f"Project with id '{id}' not found.")
    db.delete(project)
    db.commit()


@router.get("/{project_id}/tasks")
def get_project_tasks(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    """Retrieve all tasks belonging to a specific project (SPEC.md §4.3)."""
    stmt = select(ProjectModel).where(ProjectModel.id == project_id).options(selectinload(ProjectModel.tasks))
    project = db.scalars(stmt).first()
    if not project:
        raise NotFoundException(f"Project with id '{project_id}' not found.")

    tasks_data = [
        TaskResponseSchema.model_validate(t).model_dump(by_alias=True)
        for t in project.tasks
    ]
    return {"data": tasks_data}
