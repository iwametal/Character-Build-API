"""SQLAlchemy 2.0 ORM entities for Character Build API v2.

Adheres strictly to STYLEGUIDE.md, SPEC.md, and character_build.openapi.json.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.database import Base


# ============================================================================
# Security & Authentication Models
# ============================================================================


class UserModel(Base):
    """User account entity for JWT and RBAC authentication."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="MEMBER")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


# ============================================================================
# TaskFlow / Project & Task Models (STYLEGUIDE.md & SPEC.md 1:N Relationship)
# ============================================================================


class ProjectModel(Base):
    """Project entity with 1:N relationship to tasks."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    tasks: Mapped[list["TaskModel"]] = relationship(
        "TaskModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class TaskModel(Base):
    """Task entity belonging to a project."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="TODO")
    priority: Mapped[str] = mapped_column(String(50), default="MEDIUM")
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    project_id: Mapped[str | None] = mapped_column(
        ForeignKey("projects.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    project: Mapped[Optional["ProjectModel"]] = relationship(
        "ProjectModel",
        back_populates="tasks",
    )


# ============================================================================
# Reference & Catalog Models
# ============================================================================


class GenderModel(Base):
    """Gender reference entity."""

    __tablename__ = "genders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    gender: Mapped[str] = mapped_column(String(50), nullable=False)


class RarityModel(Base):
    """Item rarity scale entity."""

    __tablename__ = "rarities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rarity: Mapped[str] = mapped_column(String(50), nullable=False)


class BodyPartModel(Base):
    """Equippable body part slot."""

    __tablename__ = "body_parts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    body_part: Mapped[str] = mapped_column(String(50), nullable=False)


class StatusEffectModel(Base):
    """Status effect applied in battle."""

    __tablename__ = "status_effects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)


class ElementModel(Base):
    """Elemental affinity reference with self-referential relationships."""

    __tablename__ = "elements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    element: Mapped[str] = mapped_column(String(50), nullable=False)
    strength_id: Mapped[int | None] = mapped_column(
        ForeignKey("elements.id"),
        nullable=True,
    )
    weakness_id: Mapped[int | None] = mapped_column(
        ForeignKey("elements.id"),
        nullable=True,
    )

    strength_rel: Mapped[Optional["ElementModel"]] = relationship(
        "ElementModel",
        foreign_keys=[strength_id],
        remote_side=[id],
    )
    weakness_rel: Mapped[Optional["ElementModel"]] = relationship(
        "ElementModel",
        foreign_keys=[weakness_id],
        remote_side=[id],
    )

    @property
    def strength(self) -> int | None:
        return self.strength_id

    @property
    def weakness(self) -> int | None:
        return self.weakness_id



class JobModel(Base):
    """Job / class attributes entity."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job: Mapped[str] = mapped_column(String(100), nullable=False)
    atk: Mapped[int] = mapped_column(Integer, default=0)
    def_: Mapped[int] = mapped_column("def", Integer, default=0)
    hp: Mapped[int] = mapped_column(Integer, default=0)
    vigor: Mapped[int] = mapped_column(Integer, default=0)
    intelligence: Mapped[int] = mapped_column(Integer, default=0)


class RaceModel(Base):
    """Character/monster race entity."""

    __tablename__ = "races"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    race: Mapped[str] = mapped_column(String(100), nullable=False)
    atk: Mapped[int] = mapped_column(Integer, default=0)
    def_: Mapped[int] = mapped_column("def", Integer, default=0)
    hp: Mapped[int] = mapped_column(Integer, default=0)
    intelligence: Mapped[int] = mapped_column(Integer, default=0)
    mana: Mapped[int] = mapped_column(Integer, default=0)
    vigor: Mapped[int] = mapped_column(Integer, default=0)


# ============================================================================
# Abilities, Magic & Combat Models
# ============================================================================


class PhysicalAbilityModel(Base):
    """Physical combat skill entity."""

    __tablename__ = "physical_abilities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    damage: Mapped[int] = mapped_column(Integer, default=0)
    lv_required: Mapped[int] = mapped_column(Integer, default=1)
    shield: Mapped[int] = mapped_column(Integer, default=0)
    status_id: Mapped[int | None] = mapped_column(
        ForeignKey("status_effects.id"),
        nullable=True,
    )

    status: Mapped[Optional["StatusEffectModel"]] = relationship(
        "StatusEffectModel"
    )


class MagicModel(Base):
    """Magic spell / skill entity."""

    __tablename__ = "magics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    magic: Mapped[str] = mapped_column(String(100), nullable=False)
    damage: Mapped[int] = mapped_column(Integer, default=0)
    lv_required: Mapped[int] = mapped_column(Integer, default=1)
    mana_consumption: Mapped[int] = mapped_column(Integer, default=0)
    shield: Mapped[int] = mapped_column(Integer, default=0)
    element_id: Mapped[int] = mapped_column(
        ForeignKey("elements.id"),
        nullable=False,
    )
    status_id: Mapped[int | None] = mapped_column(
        ForeignKey("status_effects.id"),
        nullable=True,
    )

    element: Mapped["ElementModel"] = relationship("ElementModel")
    status: Mapped[Optional["StatusEffectModel"]] = relationship(
        "StatusEffectModel"
    )


class ArmorModel(Base):
    """Armor equipment entity."""

    __tablename__ = "armors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    body_part_id: Mapped[int] = mapped_column(
        ForeignKey("body_parts.id"),
        nullable=False,
    )
    atk: Mapped[int] = mapped_column(Integer, default=0)
    def_: Mapped[int] = mapped_column("def", Integer, default=0)
    hp: Mapped[int] = mapped_column(Integer, default=0)
    intelligence: Mapped[int] = mapped_column(Integer, default=0)
    vigor: Mapped[int] = mapped_column(Integer, default=0)
    rarity_id: Mapped[int] = mapped_column(
        ForeignKey("rarities.id"),
        nullable=False,
    )

    body_part: Mapped["BodyPartModel"] = relationship("BodyPartModel")
    rarity: Mapped["RarityModel"] = relationship("RarityModel")


class WeaponModel(Base):
    """Weapon equipment entity."""

    __tablename__ = "weapons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    atk: Mapped[int] = mapped_column(Integer, default=0)
    def_: Mapped[int] = mapped_column("def", Integer, default=0)
    hp: Mapped[int] = mapped_column(Integer, default=0)
    intelligence: Mapped[int] = mapped_column(Integer, default=0)
    vigor: Mapped[int] = mapped_column(Integer, default=0)
    magic_id: Mapped[int | None] = mapped_column(
        ForeignKey("magics.id"),
        nullable=True,
    )

    magic: Mapped[Optional["MagicModel"]] = relationship("MagicModel")


# ============================================================================
# Central Entities: Character, Monster & Abilities
# ============================================================================


class CharacterModel(Base):
    """Character entity."""

    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1)
    extra_mana: Mapped[int] = mapped_column(Integer, default=0)
    gender_id: Mapped[int] = mapped_column(
        ForeignKey("genders.id"),
        nullable=False,
    )
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False,
    )
    race_id: Mapped[int] = mapped_column(
        ForeignKey("races.id"),
        nullable=False,
    )

    gender: Mapped["GenderModel"] = relationship("GenderModel")
    job: Mapped["JobModel"] = relationship("JobModel")
    race: Mapped["RaceModel"] = relationship("RaceModel")
    abilities: Mapped[list["AbilityModel"]] = relationship(
        "AbilityModel",
        back_populates="character",
        cascade="all, delete-orphan",
    )


class AbilityModel(Base):
    """Association of character to magic and physical skills."""

    __tablename__ = "abilities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    character_id: Mapped[str] = mapped_column(
        ForeignKey("characters.id"),
        nullable=False,
    )
    magic_id: Mapped[int | None] = mapped_column(
        ForeignKey("magics.id"),
        nullable=True,
    )
    physical_id: Mapped[int | None] = mapped_column(
        ForeignKey("physical_abilities.id"),
        nullable=True,
    )

    character: Mapped["CharacterModel"] = relationship(
        "CharacterModel",
        back_populates="abilities",
    )
    magic: Mapped[Optional["MagicModel"]] = relationship("MagicModel")
    physical: Mapped[Optional["PhysicalAbilityModel"]] = relationship(
        "PhysicalAbilityModel"
    )


class MonsterModel(Base):
    """Monster entity."""

    __tablename__ = "monsters"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    race_id: Mapped[int | None] = mapped_column(
        ForeignKey("races.id"),
        nullable=True,
    )
    atk: Mapped[int] = mapped_column(Integer, default=0)
    def_: Mapped[int] = mapped_column("def", Integer, default=0)
    hp: Mapped[int] = mapped_column(Integer, default=0)
    intelligence: Mapped[int] = mapped_column(Integer, default=0)
    vigor: Mapped[int] = mapped_column(Integer, default=0)

    race: Mapped[Optional["RaceModel"]] = relationship("RaceModel")
