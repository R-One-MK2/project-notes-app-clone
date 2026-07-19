"""SQLAlchemy adapter for NoteRepository port."""

from uuid import UUID

from app.notes.models import Note
from app.notes.repositories.mappers import note_from_orm, note_to_orm
from app.notes.repositories.orm import NoteORM


class SQLAlchemyNoteRepository:
    """
    Real NoteRepository backed by SQLAlchemy.

    Satisfies the NoteRepository port structurally (duck typing via Protocol).

    Each instance holds a session for the duration of a unit of work.
    """

    def __init__(self, session) -> None:
        self._session = session

    def save(self, note: Note):
        """
        Persist note. Idempotent via merge() — same primary key overwrites.
        Commits the transaction on success.
        """
        orm = note_to_orm(note)
        self._session.merge(orm)
        self._session.commit()

    def find_by_id(self, note_id: UUID) -> Note | None:
        """Retrieve note by primary key. Returns None if not found."""
        orm = self._session.get(NoteORM, note_id)
        if orm is None:
            return None
        return note_from_orm(orm)
