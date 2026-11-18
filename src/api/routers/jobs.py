"""Jobs router: /api/v1/jobs."""

from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.exceptions import NotFoundException
from src.api.models import JobModel
from src.api.schemas import JobAttributesSchema, JobResponseSchema
from src.api.security import require_role

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])


@router.get("", response_model=list[JobAttributesSchema])
def list_jobs(db: Annotated[Session, Depends(get_db)]) -> list[JobModel]:
    """Retrieve all jobs."""
    return db.query(JobModel).all()


@router.post("", response_model=JobAttributesSchema, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobAttributesSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> JobModel:
    """Create a new job."""
    job = JobModel(
        job=payload.job,
        atk=payload.atk,
        def_=payload.def_,
        hp=payload.hp,
        vigor=payload.vigor,
        intelligence=payload.intelligence,
    )
    if payload.id is not None:
        job.id = payload.id
    db.add(job)
    db.commit()
    db.refresh(job)
    response.headers["Location"] = f"/api/v1/jobs/{job.id}"
    return job


@router.get("/{id}", response_model=JobAttributesSchema)
def get_job(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> JobModel:
    """Retrieve a job by ID."""
    job = db.query(JobModel).filter(JobModel.id == id).first()
    if not job:
        raise NotFoundException(f"Job with id '{id}' not found.")
    return job


@router.put("/{id}", response_model=JobAttributesSchema)
def update_job(
    id: int,
    payload: JobAttributesSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> JobModel:
    """Update a job by ID."""
    job = db.query(JobModel).filter(JobModel.id == id).first()
    if not job:
        raise NotFoundException(f"Job with id '{id}' not found.")
    job.job = payload.job
    job.atk = payload.atk
    job.def_ = payload.def_
    job.hp = payload.hp
    job.vigor = payload.vigor
    job.intelligence = payload.intelligence
    db.commit()
    db.refresh(job)
    return job


@router.patch("/{id}", response_model=JobAttributesSchema)
def patch_job(
    id: int,
    payload: JobAttributesSchema,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN", "MEMBER"))],
) -> JobModel:
    """Partially update a job by ID."""
    job = db.query(JobModel).filter(JobModel.id == id).first()
    if not job:
        raise NotFoundException(f"Job with id '{id}' not found.")
    fields = payload.model_dump(exclude_unset=True, by_alias=False)
    for field, value in fields.items():
        if field == "id" or value is None:
            continue
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[object, Depends(require_role("ADMIN"))],
) -> None:
    """Delete a job by ID (ADMIN only)."""
    job = db.query(JobModel).filter(JobModel.id == id).first()
    if not job:
        raise NotFoundException(f"Job with id '{id}' not found.")
    db.delete(job)
    db.commit()
