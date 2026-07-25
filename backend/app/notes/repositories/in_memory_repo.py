"""In-memory implementation of NoteRepository (for testing)."""

from uuid import UUID

from app.notes.models import Note


class InMemoryNoteRepository:
    """Fake NoteRepository using a dict. For testing only."""

    def __init__(self) -> None:
        self._notes: dict[UUID, Note] = {}

    def save(self, note: Note):
        """Save is idempotent: writing an existing note overwrites."""
        self._notes[note.note_id] = note

    def find_by_id(self, note_id: UUID) -> Note | None:
        return self._notes.get(note_id)
