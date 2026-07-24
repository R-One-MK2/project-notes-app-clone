"""Shared pytest fixtures for the entire test suite."""

from collections.abc import Iterator

import pytest
from app.database.base import Base

# Import ORM models to register them with Base.metadata.
# These imports look unused but are essential for create_all() to work.
from app.notes.repositories.orm import NoteORM  # noqa: F401
from app.organization.repositories.orm import FolderORM  # noqa: F401
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def db_session() -> Iterator[Session]:
    """
    Provide a fresh in-memory SQLite session for each test.

    Total isolation:
    - New engine per test
    - Fresh schema per test
    - No shared state between tests
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
