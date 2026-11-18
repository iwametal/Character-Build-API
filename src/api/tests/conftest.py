"""Pytest fixtures for Character Build API v2.

Provides an isolated in-memory SQLite database per test, dependency overrides,
and pre-minted JWT authorization headers for ADMIN and MEMBER roles.
"""

from __future__ import annotations

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.database import Base, get_db, seed_data
from src.api.main import app
from src.api.models import UserModel
from src.api.security import create_access_token


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provide a fresh, isolated in-memory SQLite database populated with seed data."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    session = TestingSession()
    seed_data(session)

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient configured with overridden get_db dependency pointing to the isolated session."""
    def _override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session: Session) -> UserModel:
    """Retrieve the seeded ADMIN user."""
    user = db_session.query(UserModel).filter(UserModel.email == "admin@fatec.sp.gov.br").first()
    assert user is not None, "Seeded admin user not found in test database"
    return user


@pytest.fixture
def member_user(db_session: Session) -> UserModel:
    """Retrieve the seeded MEMBER user."""
    user = db_session.query(UserModel).filter(UserModel.email == "aluno@fatec.sp.gov.br").first()
    assert user is not None, "Seeded member user not found in test database"
    return user


@pytest.fixture
def admin_token(admin_user: UserModel) -> str:
    """Mint a valid JWT for the ADMIN user."""
    return create_access_token(sub=admin_user.id, email=admin_user.email, role="ADMIN")


@pytest.fixture
def member_token(member_user: UserModel) -> str:
    """Mint a valid JWT for the MEMBER user."""
    return create_access_token(sub=member_user.id, email=member_user.email, role="MEMBER")


@pytest.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    """Bearer authorization header for ADMIN."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def member_headers(member_token: str) -> dict[str, str]:
    """Bearer authorization header for MEMBER."""
    return {"Authorization": f"Bearer {member_token}"}
