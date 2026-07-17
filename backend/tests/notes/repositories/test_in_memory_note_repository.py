"""
Tests for the in-memory note repository.

SESSION 4 — Repository Adapters (Part B: Note)
Goal: Fake NoteRepository for testing service business logic.

Cycles:
  [x] Cycle 24: save() persists a note
  [x] Cycle 25: find_by_id() retrieves a saved note
  [x] Cycle 26: find_by_id() returns None for unknown ID
  [x] Cycle 27: save() is idempotent (writing twice doesn't duplicate)
"""

from uuid import uuid4

from app.notes.models import Note
from app.notes.repositories import InMemoryNoteRepository

USER_ID = uuid4()
FOLDER_ID = uuid4()


def test_save_persists_a_note():
    """
    Repository contract: save stores the note for later retrieval.
    """
    repo = InMemoryNoteRepository()
    note = Note.create(USER_ID, FOLDER_ID, "sample title", "sample content")

    repo.save(note)

    retrieved = repo.find_by_id(note.note_id)

    assert retrieved is not None
    assert note.note_id == retrieved.note_id


def test_find_by_id_retrieves_saved_note():
    """
    Repository contract: find_by_id returns the exact stored note
    """

    repo = InMemoryNoteRepository()
    note = Note.create(USER_ID, FOLDER_ID, "sample title", "sample content")

    repo.save(note)

    retrieved = repo.find_by_id(note.note_id)

    assert retrieved == note


def test_find_by_id_returns_none_for_unknown_id():
    """
    Repository contract: find_by_id returns None for unknown IDs.
    """
    repo = InMemoryNoteRepository()

    retrieved = repo.find_by_id(uuid4())

    assert retrieved is None


def test_is_idempotent():
    """
    Repository contract: saving the same note twice does not duplicate.

    A single note_id maps to a single note, regardless of save frequency.

    Later saves overwrite (useful for future update flows).
    """
    repo = InMemoryNoteRepository()

    note = Note.create(USER_ID, FOLDER_ID, "sample title", "sample content")

    repo.save(note)
    repo.save(note)

    retrieved = repo.find_by_id(note.note_id)

    assert retrieved == note
