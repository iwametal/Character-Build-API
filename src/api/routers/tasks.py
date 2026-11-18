"""Tasks router: /api/v1/tasks."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import ProjectModel, TaskModel
from src.api.schemas import TaskResponseSchema, TaskSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.get("", response_model=list[TaskResponseSchema])
def list_tasks(
    db: Annotated[Session, Depends(get_db)],
    task_status: Annotated[str | None, Query(alias="status")] = None,
    priority: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[TaskModel]:
    """Retrieve tasks with optional pagination, filters, and preloaded project relation."""
    stmt = select(TaskModel).options(selectinload(TaskModel.project))

    if task_status:
        stmt = stmt.where(TaskModel.status == task_status)
    if priority:
        stmt = stmt.where(TaskModel.priority == priority)
    if search:
        search_pattern = f"%{search.lower()}%"
        stmt = stmt.where(
            or_(
                TaskModel.title.ilike(search_pattern),
                TaskModel.description.ilike(search_pattern),
            )
        )

    stmt = stmt.offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


@router.post("", response_model=TaskResponseSchema, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> TaskModel:
    """Create a new task, validating project existence if specified."""
    if payload.project_id:
        proj = db.query(ProjectModel).filter(ProjectModel.id == payload.project_id).first()
        if not proj:
            raise NotFoundException(f"Project with id '{payload.project_id}' not found.")

    task_id = payload.id or str(uuid.uuid4())
    task = TaskModel(
        id=task_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
        project_id=payload.project_id,
    )
    db.add(task)
    db.commit()

    stmt = select(TaskModel).where(TaskModel.id == task.id).options(selectinload(TaskModel.project))
    loaded = db.scalars(stmt).first()
    response.headers["Location"] = f"/api/v1/tasks/{task.id}"
    return loaded  # type: ignore[return-value]


@router.get("/{id}", response_model=TaskResponseSchema)
def get_task(
    id: str,
    db: Annotated[Session, Depends(get_db)],
) -> TaskModel:
    """Retrieve a single task by ID."""
    stmt = select(TaskModel).where(TaskModel.id == id).options(selectinload(TaskModel.project))
    task = db.scalars(stmt).first()
    if not task:
        raise NotFoundException(f"Task with id '{id}' not found.")
    return task


@router.put("/{id}", response_model=TaskResponseSchema)
def update_task(
    id: str,
    payload: TaskSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> TaskModel:
    """Update a task completely."""
    task = db.query(TaskModel).filter(TaskModel.id == id).first()
    if not task:
        raise NotFoundException(f"Task with id '{id}' not found.")

    if payload.project_id:
        proj = db.query(ProjectModel).filter(ProjectModel.id == payload.project_id).first()
        if not proj:
            raise NotFoundException(f"Project with id '{payload.project_id}' not found.")

    task.title = payload.title
    task.description = payload.description
    task.status = payload.status
    task.priority = payload.priority
    task.due_date = payload.due_date
    task.project_id = payload.project_id
    task.updated_at = datetime.utcnow()
    db.commit()

    stmt = select(TaskModel).where(TaskModel.id == id).options(selectinload(TaskModel.project))
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.patch("/{id}", response_model=TaskResponseSchema)
def patch_task(
    id: str,
    payload: TaskSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> TaskModel:
    """Update a task partially."""
    task = db.query(TaskModel).filter(TaskModel.id == id).first()
    if not task:
        raise NotFoundException(f"Task with id '{id}' not found.")

    if payload.title:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.status:
        task.status = payload.status
    if payload.priority:
        task.priority = payload.priority
    if payload.due_date is not None:
        task.due_date = payload.due_date
    if payload.project_id is not None:
        proj = db.query(ProjectModel).filter(ProjectModel.id == payload.project_id).first()
        if not proj:
            raise NotFoundException(f"Project with id '{payload.project_id}' not found.")
        task.project_id = payload.project_id

    task.updated_at = datetime.utcnow()
    db.commit()

    stmt = select(TaskModel).where(TaskModel.id == id).options(selectinload(TaskModel.project))
    return db.scalars(stmt).first()  # type: ignore[return-value]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a task (ADMIN only)."""
    task = db.query(TaskModel).filter(TaskModel.id == id).first()
    if not task:
        raise NotFoundException(f"Task with id '{id}' not found.")
    db.delete(task)
    db.commit()
