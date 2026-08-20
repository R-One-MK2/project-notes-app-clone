"""Ports (interfaces) for the notes context."""

from typing import Protocol
from uuid import UUID

from app.notes.models import Note


class NoteRepository(Protocol):
    """
    Port: interface any note repository must implement.

    Adapters:
    - InMemoryNoteRepository (Session 4, for testing)
    - SQLAlchemyNoteRepository (Session 5, for production)
    """

    def save(self, note: Note) -> None:
        """
        Persist a note. Idempotent — saving twice is safe (updates).
        """
        ...

    def find_by_id(self, note_id: UUID) -> Note | None:
        """
        Retrieve a note by ID. Returns None if not found
        """
        ...

    def find_by_user(self, user_id: UUID) -> list[Note]:
        """
        Retrieve all notes owned by user_id.
        Returns an empty list if the user has no notes.
        """
        ...
