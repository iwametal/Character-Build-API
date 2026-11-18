"""Database engine, session management, and seed data initialization."""

from __future__ import annotations

import os
from collections.abc import Generator
import bcrypt
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./character-build.db")

# Ensure directory for SQLite database exists if specified in path
if DATABASE_URL.startswith("sqlite:////"):
    _db_path = DATABASE_URL.replace("sqlite:////", "/")
    _dir = os.path.dirname(_db_path)
    if _dir:
        os.makedirs(_dir, exist_ok=True)
elif DATABASE_URL.startswith("sqlite:///"):
    _db_path = DATABASE_URL.replace("sqlite:///", "")
    _dir = os.path.dirname(_db_path)
    if _dir:
        os.makedirs(_dir, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30.0}
    if DATABASE_URL.startswith("sqlite")
    else {},
)

# Enable WAL mode and busy timeout for concurrent SQLite access across instances
if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout=30000;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy 2.0 ORM entities."""

    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    """Generate bcrypt password hash."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def seed_data(db: Session) -> None:
    """Populate database with default users and reference catalog data idempotently."""
    from src.api.models import (
        BodyPartModel,
        ElementModel,
        GenderModel,
        JobModel,
        MagicModel,
        PhysicalAbilityModel,
        RaceModel,
        RarityModel,
        StatusEffectModel,
        UserModel,
    )

    # 1. Seed Users (Admin & Member)
    admin_email = "admin@fatec.sp.gov.br"
    admin_user = db.query(UserModel).filter(UserModel.email == admin_email).first()
    if not admin_user:
        admin_user = UserModel(
            name="Administrador FATEC",
            email=admin_email,
            hashed_password=hash_password("Admin@2026"),
            role="ADMIN",
        )
        db.add(admin_user)
    else:
        admin_user.role = "ADMIN"
        admin_user.hashed_password = hash_password("Admin@2026")

    member_email = "aluno@fatec.sp.gov.br"
    member_user = db.query(UserModel).filter(UserModel.email == member_email).first()
    if not member_user:
        member_user = UserModel(
            name="Aluno FATEC",
            email=member_email,
            hashed_password=hash_password("Aluno@2026"),
            role="MEMBER",
        )
        db.add(member_user)
    else:
        member_user.role = "MEMBER"
        member_user.hashed_password = hash_password("Aluno@2026")

    # 2. Seed Genders
    genders = [(1, "Masculino"), (2, "Feminino"), (3, "Outro")]
    for gid, gname in genders:
        if not db.query(GenderModel).filter(GenderModel.id == gid).first():
            db.add(GenderModel(id=gid, gender=gname))

    # 3. Seed Rarities
    rarities = [(1, "Comum"), (2, "Incomum"), (3, "Raro"), (4, "Épico"), (5, "Lendário")]
    for rid, rname in rarities:
        if not db.query(RarityModel).filter(RarityModel.id == rid).first():
            db.add(RarityModel(id=rid, rarity=rname))

    # 4. Seed Body Parts
    body_parts = [(1, "Cabeça"), (2, "Tronco"), (3, "Braços"), (4, "Pernas"), (5, "Pés")]
    for bpid, bpname in body_parts:
        if not db.query(BodyPartModel).filter(BodyPartModel.id == bpid).first():
            db.add(BodyPartModel(id=bpid, body_part=bpname))

    # 5. Seed Status Effects
    status_effects = [
        (1, "Queimadura", 3),
        (2, "Congelamento", 2),
        (3, "Envenenamento", 4),
        (4, "Atordoamento", 1),
    ]
    for seid, sname, dur in status_effects:
        if not db.query(StatusEffectModel).filter(StatusEffectModel.id == seid).first():
            db.add(StatusEffectModel(id=seid, status=sname, duration=dur))

    # 6. Seed Elements
    elements = [(1, "Fogo"), (2, "Água"), (3, "Terra"), (4, "Vento")]
    for eid, ename in elements:
        if not db.query(ElementModel).filter(ElementModel.id == eid).first():
            db.add(ElementModel(id=eid, element=ename))

    # 7. Seed Jobs
    jobs = [
        (1, "Guerreiro", 15, 12, 120, 14, 6),
        (2, "Mago", 6, 4, 70, 8, 18),
        (3, "Ladino", 12, 8, 90, 12, 10),
        (4, "Clérigo", 9, 10, 100, 10, 14),
    ]
    for jid, jname, atk, def_, hp, vigor, intel in jobs:
        if not db.query(JobModel).filter(JobModel.id == jid).first():
            db.add(
                JobModel(
                    id=jid,
                    job=jname,
                    atk=atk,
                    def_=def_,
                    hp=hp,
                    vigor=vigor,
                    intelligence=intel,
                )
            )

    # 8. Seed Races
    races = [
        (1, "Humano", 10, 10, 100, 10, 50, 10),
        (2, "Elfo", 8, 8, 85, 8, 80, 14),
        (3, "Anão", 12, 14, 115, 12, 30, 8),
        (4, "Orc", 16, 12, 130, 15, 20, 6),
    ]
    for rid, rname, atk, def_, hp, vigor, mana, intel in races:
        if not db.query(RaceModel).filter(RaceModel.id == rid).first():
            db.add(
                RaceModel(
                    id=rid,
                    race=rname,
                    atk=atk,
                    def_=def_,
                    hp=hp,
                    vigor=vigor,
                    mana=mana,
                    intelligence=intel,
                )
            )

    # 9. Seed Sample Magic Ability
    if not db.query(MagicModel).filter(MagicModel.id == 1).first():
        db.add(
            MagicModel(
                id=1,
                magic="Bola de Fogo",
                damage=30,
                element_id=1,
                lv_required=1,
                mana_consumption=12,
                shield=0,
                status_id=1,
            )
        )

    # 10. Seed Sample Physical Ability
    if not db.query(PhysicalAbilityModel).filter(PhysicalAbilityModel.id == 1).first():
        db.add(
            PhysicalAbilityModel(
                id=1,
                damage=25,
                lv_required=1,
                shield=5,
                status_id=None,
            )
        )

    db.commit()


def init_db() -> None:
    """Create all tables in the database and run seed data."""
    import src.api.models  # noqa: F401 - ensure all ORM models are registered

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_data(db)
