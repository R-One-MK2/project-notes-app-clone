"""FastAPI dependency-injection helpers for the database."""

from typing import Iterator

from sqlalchemy.orm import Session

from app.database.engine import SessionFactory


def get_session() -> Iterator[Session]:
    """
    Yield a database session; close after request.

    Used with FastAPI's Depends():
        def create_note(session: Session = Depends(get_session)):
            ...

    The yield pattern ensures the session closes even if the route raises.
    """
    session = SessionFactory()

    try:
        yield session
    finally:
        session.close()
