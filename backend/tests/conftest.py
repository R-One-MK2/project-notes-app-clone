"""Shared pytest fixtures for the entire test suite."""

from collections.abc import Iterator
from uuid import UUID

import pytest
from app.database.base import Base
from app.database.dependencies import get_session
from app.main import app
from app.notes.api.v1.router import get_current_user_id

# Import ORM models to register them with Base.metadata.
# These imports look unused but are essential for create_all() to work.
from app.notes.repositories.orm import NoteORM  # noqa: F401
from app.organization.models import Folder
from app.organization.repositories.mappers import folder_to_orm
from app.organization.repositories.orm import FolderORM  # noqa: F401
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# --- Constants for API tests ---

TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
TEST_FOLDER_ID = UUID("550e8400-e29b-41d4-a716-446655440000")


# --- Helper: build a fresh isolated in-memory engine ---


def _make_test_engine() -> Engine:
    """Fresh in-memory SQLite engine using StaticPool for cross-thread sharing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


# --- Fixture: raw session (for repository tests) ---


@pytest.fixture
def db_session() -> Iterator[Session]:
    """
    Provide a fresh in-memory SQLite session for each test.

    Total isolation:
    - New engine per test
    - Fresh schema per test
    - No shared state between tests
    """
    engine = _make_test_engine()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


# --- Fixture: TestClient with overrides (for API tests) ---


@pytest.fixture
def client() -> Iterator[TestClient]:
    """
    TestClient with an isolated in-memory DB and a pre-populated folder
    owned by TEST_USER_ID. Cleaned up after each test.
    """
    engine = _make_test_engine()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def override_get_current_user_id() -> UUID:
        return TEST_USER_ID

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    # Pre-populate a folder owned by TEST_USER_ID
    with SessionLocal() as setup_session:
        setup_session.add(folder_to_orm(Folder(TEST_FOLDER_ID, TEST_USER_ID)))
        setup_session.commit()

    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
