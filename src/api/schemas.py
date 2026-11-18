"""Pydantic v2 schemas for Character Build API v2.

Matches contracts from files/character_build.openapi.json, files/SPEC.md,
and files/STYLEGUIDE.md.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class AppBaseModel(BaseModel):
    """Base schema with ORM and alias compatibility."""

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


# ============================================================================
# Security, Auth & RFC 9457 Schemas
# ============================================================================


class UserRole(str, Enum):
    """Role-based access control roles."""

    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class InvalidParam(AppBaseModel):
    """Single invalid parameter report compliant with RFC 9457."""

    name: str
    reason: str


class ApiError(AppBaseModel):
    """RFC 9457 compliant error structure."""

    type: str
    title: str
    status: int
    detail: str
    instance: str
    invalid_params: list[InvalidParam] | None = Field(
        default=None,
        validation_alias=AliasChoices("invalid_params", "invalidParams"),
        serialization_alias="invalidParams",
    )

    @property
    def invalidParams(self) -> list[InvalidParam] | None:
        return self.invalid_params


class ErrorResponseSchema(AppBaseModel):
    """Legacy/Apidog error response compatibility model."""

    status: int
    code: str
    message: str
    details: dict[str, Any] | None = None


class LoginRequestDTO(AppBaseModel):
    """Credentials for authentication."""

    email: str | None = None
    username: str | None = None
    password: str = Field(..., min_length=6)


LoginRequestSchema = LoginRequestDTO


class UserResponse(AppBaseModel):
    """Authenticated user presentation DTO."""

    id: str
    name: str
    email: str
    role: UserRole


class TokenResponseDTO(AppBaseModel):
    """JWT Bearer token response."""

    access_token: str = Field(
        ...,
        validation_alias=AliasChoices("access_token", "accessToken"),
        serialization_alias="accessToken",
    )
    token_type: str = Field(
        default="bearer",
        validation_alias=AliasChoices("token_type", "tokenType"),
        serialization_alias="tokenType",
    )
    expires_in: int = Field(
        default=3600,
        validation_alias=AliasChoices("expires_in", "expiresIn"),
        serialization_alias="expiresIn",
    )
    user: UserResponse | None = None

    @property
    def accessToken(self) -> str:
        return self.access_token

    @property
    def tokenType(self) -> str:
        return self.token_type

    @property
    def expiresIn(self) -> int:
        return self.expires_in


LoginResponseSchema = TokenResponseDTO


# ============================================================================
# Reference & Catalog Schemas
# ============================================================================


class GenderSchema(AppBaseModel):
    """Gender reference entity."""

    id: int | None = None
    gender: str


class RaritySchema(AppBaseModel):
    """Item rarity scale entity."""

    id: int | None = None
    rarity: str


class BodyPartSchema(AppBaseModel):
    """Equippable body part slot."""

    id: int | None = None
    body_part: str = Field(
        ...,
        validation_alias=AliasChoices("body_part", "bodyPart"),
        serialization_alias="body_part",
    )


class StatusEffectSchema(AppBaseModel):
    """Status effect applied in battle."""

    id: int | None = None
    status: str
    duration: int | None = None


class ElementSchema(AppBaseModel):
    """Elemental affinity reference (IDs for creation/update)."""

    id: int | None = None
    element: str
    strength: int | None = None
    weakness: int | None = None


class ElementResponseSchema(AppBaseModel):
    """Elemental affinity response with nested relationship representations."""

    id: int
    element: str
    strength: ElementSchema | None = None
    weakness: ElementSchema | None = None


class JobAttributesSchema(AppBaseModel):
    """Job / class attributes schema for creation and input."""

    id: int | None = None
    job: str
    atk: int = 0
    def_: int = Field(
        default=0,
        validation_alias=AliasChoices("def", "def_"),
        serialization_alias="def",
    )
    hp: int = 0
    vigor: int = 0
    intelligence: int = 0


class JobResponseSchema(AppBaseModel):
    """Job attributes response presentation."""

    id: int
    job: str
    atk: int
    def_: int = Field(
        ...,
        validation_alias=AliasChoices("def", "def_"),
        serialization_alias="def",
    )
    hp: int
    intelligence: int
    vigor: int


class RaceSchema(AppBaseModel):
    """Character/monster race schema for input."""

    id: int | None = None
    race: str
    atk: int = 0
    def_: int = Field(
        default=0,
        validation_alias=AliasChoices("def", "def_"),
        serialization_alias="def",
    )
    hp: int = 0
    intelligence: int = 0
    mana: int = 0
    vigor: int = 0


class RaceResponseSchema(AppBaseModel):
    """Character/monster race response representation."""

    id: int
    race: str
    atk: int
    def_: int = Field(
        ...,
        validation_alias=AliasChoices("def", "def_"),
        serialization_alias="def",
    )
    hp: int
    intelligence: int
    mana: int
    vigor: int


# ============================================================================
# Abilities, Magic & Combat Schemas
# ============================================================================


class PhysicalAbilitySchema(AppBaseModel):
    """Physical combat skill input schema."""

    id: int | None = None
    damage: int
    lv_required: int = Field(
        ...,
        validation_alias=AliasChoices("lv_required", "lvRequired"),
        serialization_alias="lv_required",
    )
    shield: int = 0
    status: int | None = None


class PhysicalAbilityResponseSchema(AppBaseModel):
    """Physical combat skill response schema."""

    id: int
    damage: int
    lv_required: int = Field(
        ...,
        validation_alias=AliasChoices("lv_required", "lvRequired"),
        serialization_alias="lv_required",
    )
    shield: int = 0
    status: StatusEffectSchema | None = None


class MagicAbilitySchema(AppBaseModel):
    """Magic spell / skill input schema."""

    id: int | None = None
    magic: str
    damage: int
    element: int
    lv_required: int = Field(
        ...,
        validation_alias=AliasChoices("lv_required", "lvRequired"),
        serialization_alias="lv_required",
    )
    mana_consumption: int = Field(
        ...,
        validation_alias=AliasChoices("mana_consumption", "manaConsumption"),
        serialization_alias="mana_consumption",
    )
    shield: int = 0
    status: int | None = None


class MagicAbilityResponseSchema(AppBaseModel):
    """Magic spell / skill response representation."""

    id: int
    magic: str
    damage: int
    element: ElementSchema | None = None
    lv_required: int = Field(
        ...,
        validation_alias=AliasChoices("lv_required", "lvRequired"),
        serialization_alias="lv_required",
    )
    mana_consumption: int = Field(
        ...,
        validation_alias=AliasChoices("mana_consumption", "manaConsumption"),
        serialization_alias="mana_consumption",
    )
    shield: int = 0
    status: StatusEffectSchema | None = None


MagicResponseSchema = MagicAbilityResponseSchema


class ArmorSchema(AppBaseModel):
    """Armor equipment input schema."""

    id: int | None = None
    body_part: int = Field(
        ...,
        validation_alias=AliasChoices("body_part", "bodyPart"),
        serialization_alias="body_part",
    )
    atk: int = 0
    def_: int = Field(
        default=0,
        validation_alias=AliasChoices("def", "def_"),
        serialization_alias="def",
    )
    hp: int = 0
    intelligence: int = 0
    vigor: int = 0
    rarity: int


class ArmorResponseSchema(AppBaseModel):
    """Armor equipment response representation."""

    id: int
    body_part: BodyPartSchema | None = Field(
        default=None,
        validation_alias=AliasChoices("body_part", "bodyPart"),
        serialization_alias="body_part",
    )
    atk: int
    def_: int = Field(
        ...,
        validation_alias=AliasChoices("def", "def_"),
        serialization_alias="def",
    )
    hp: int
    intelligence: int
    vigor: int
    rarity: RaritySchema | None = None


class WeaponSchema(AppBaseModel):
    """Weapon equipment input schema."""

    id: int | None = None
    name: str
    atk: int = 0
    def_: int = Field(
        default=0,
        validation_alias=AliasChoices("def", "def_"),
        serialization_alias="def",
    )
    hp: int = 0
    intelligence: int = 0
    vigor: int = 0
    magic: int | None = None


class WeaponResponseSchema(AppBaseModel):
    """Weapon equipment response representation."""

    id: int
    name: str
    atk: int
    def_: int = Field(
        ...,
        validation_alias=AliasChoices("def", "def_"),
        serialization_alias="def",
    )
    hp: int
    intelligence: int
    vigor: int
    magic: MagicAbilityResponseSchema | None = None


# ============================================================================
# Central Entities: Character & Monster
# ============================================================================


class CharacterSchema(AppBaseModel):
    """Character creation and update schema."""

    id: str | None = None
    name: str
    last_name: str = Field(
        ...,
        validation_alias=AliasChoices("last_name", "lastName"),
        serialization_alias="last_name",
    )
    age: int
    level: int
    extra_mana: int = Field(
        default=0,
        validation_alias=AliasChoices("extra_mana", "extraMana"),
        serialization_alias="extra_mana",
    )
    gender: int
    job: int
    race: int


class CharacterResponseSchema(AppBaseModel):
    """Character response schema with populated references."""

    id: str
    name: str
    last_name: str = Field(
        ...,
        validation_alias=AliasChoices("last_name", "lastName"),
        serialization_alias="last_name",
    )
    age: int
    level: int
    extra_mana: int = Field(
        default=0,
        validation_alias=AliasChoices("extra_mana", "extraMana"),
        serialization_alias="extra_mana",
    )
    gender: GenderSchema | None = None
    job: JobAttributesSchema | None = None
    race: RaceSchema | None = None


class MonsterSchema(AppBaseModel):
    """Monster entity input schema."""

    id: str | None = None
    name: str | None = None
    race: str | int | None = None
    atk: int = 0
    def_: int = Field(
        default=0,
        validation_alias=AliasChoices("def", "def_"),
        serialization_alias="def",
    )
    hp: int = 0
    intelligence: int = 0
    vigor: int = 0


class MonsterResponseSchema(AppBaseModel):
    """Monster entity response schema."""

    id: str
    name: str | None = None
    race: RaceSchema | None = None
    atk: int
    def_: int = Field(
        ...,
        validation_alias=AliasChoices("def", "def_"),
        serialization_alias="def",
    )
    hp: int
    intelligence: int
    vigor: int


class AbilitySchema(AppBaseModel):
    """Link between character and magic/physical abilities."""

    id: int | None = None
    character: str | int | None = None
    magic: int | None = None
    physical: int | None = None


class AbilityResponseSchema(AppBaseModel):
    """Ability response with fully loaded character and ability details."""

    id: int
    character: CharacterResponseSchema | None = None
    magic: MagicAbilityResponseSchema | None = None
    physical: PhysicalAbilityResponseSchema | None = None


# ============================================================================
# TaskFlow / Project & Task Schemas (STYLEGUIDE.md & SPEC.md)
# ============================================================================


class TaskSchema(AppBaseModel):
    """Task creation and update schema."""

    id: str | None = None
    title: str
    description: str | None = None
    status: str = "TODO"
    priority: str = "MEDIUM"
    due_date: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("due_date", "dueDate"),
        serialization_alias="dueDate",
    )
    project_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("project_id", "projectId"),
        serialization_alias="projectId",
    )


class TaskResponseSchema(AppBaseModel):
    """Task presentation schema with camelCase aliases."""

    id: str
    title: str
    description: str | None = None
    status: str
    priority: str
    due_date: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("due_date", "dueDate"),
        serialization_alias="dueDate",
    )
    project_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("project_id", "projectId"),
        serialization_alias="projectId",
    )
    created_at: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("created_at", "createdAt"),
        serialization_alias="createdAt",
    )
    updated_at: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("updated_at", "updatedAt"),
        serialization_alias="updatedAt",
    )


class ProjectSchema(AppBaseModel):
    """Project creation and update schema."""

    id: str | None = None
    name: str
    description: str | None = None


class ProjectResponseSchema(AppBaseModel):
    """Project presentation schema with embedded tasks."""

    id: str
    name: str
    description: str | None = None
    created_at: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("created_at", "createdAt"),
        serialization_alias="createdAt",
    )
    updated_at: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("updated_at", "updatedAt"),
        serialization_alias="updatedAt",
    )
    tasks: list[TaskResponseSchema] = []

