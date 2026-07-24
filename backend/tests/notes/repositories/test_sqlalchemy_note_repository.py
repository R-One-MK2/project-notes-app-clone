"""
Tests for SQLAlchemyNoteRepository (integration with real DB).

SESSION 5 — Persistence Adapters (Note)
Goal: Verify SQL adapter satisfies the NoteRepository port contract.

Cycles:
  [x] Cycle 36: save() persists to DB and find_by_id retrieves        → AC-21
  [x] Cycle 37: find_by_id() returns None for unknown ID              → AC-22
  [x] Cycle 38: save() is idempotent (upsert semantics)               → AC-23
  [] Cycle 39: title and content values are preserved exactly        → AC-24
"""

from uuid import uuid4

from app.notes.models import Note
from app.notes.repositories import SQLAlchemyNoteRepository
from sqlalchemy.orm import Session

USER_ID = uuid4()
FOLDER_ID = uuid4()


def test_save_and_retrieve_a_note(db_session: Session):
    """AC-21: save + find_by_id round-trip works."""

    repo = SQLAlchemyNoteRepository(db_session)
    note = Note.create(USER_ID, FOLDER_ID, "sample title", "sample content")

    repo.save(note)
    retrieved = repo.find_by_id(note.note_id)

    assert retrieved is not None
    assert retrieved == note


def test_find_by_id_returns_none_when_missing(db_session: Session):
    """AC-22: unknown ID returns None, not an exception."""
    repo = SQLAlchemyNoteRepository(db_session)

    # Unknown ID
    result = repo.find_by_id(uuid4())

    assert result is None


def test_save_is_idempotent(db_session: Session):
    """AC-23: saving twice does not duplicate."""

    repo = SQLAlchemyNoteRepository(db_session)

    note = Note.create(USER_ID, FOLDER_ID, "sample title", "sample content")

    repo.save(note)
    repo.save(note)

    retrieved = repo.find_by_id(note.note_id)
    assert retrieved == note


def test_values_preserved_across_save_and_load(db_session: Session):
    """AC-24: title/content preserved exactly across persistence boundary."""

    repo = SQLAlchemyNoteRepository(db_session)
    note = Note.create(
        USER_ID, FOLDER_ID, "sample title", "Multi line \n sample content"
    )

    repo.save(note)
    retrieved = repo.find_by_id(note.note_id)

    assert retrieved is not None
    assert retrieved.title.value == "sample title"
    assert retrieved.content.value == "Multi line \n sample content"
