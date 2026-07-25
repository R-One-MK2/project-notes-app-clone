"""Database engine and session factory."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# For development: SQLite file. For production: PostgreSQL URL via env var.
DATABASE_URL = "sqlite:///./notes.db"

engine = create_engine(
    DATABASE_URL,
    # SQLite-specific: allow multi-thread access (FastAPI uses multiple threads)
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionFactory = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,  # ORM objects usable after commit (avoids DetachedInstanceError)
)


def create_tables() -> None:
    """
    Create all tables. Call once at app startup.

    IMPORTANT: ORM models must be imported before this runs.
    Otherwise Base.metadata doesn't know about them.
    """
    from app.database.base import Base

    # Import ORM models to register them with Base.metadata.
    # These imports look unused but are essential for create_all() to work.
    from app.notes.repositories.orm import NoteORM  # noqa: F401
    from app.organization.repositories.orm import FolderORM  # noqa: F401

    Base.metadata.create_all(engine)
