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

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.notes.models import Content, Note, Title
from app.notes.repositories import SQLAlchemyNoteRepository
from sqlalchemy.orm import Session

USER_ID = uuid4()
OTHER_USER_ID = uuid4()
FOLDER_ID = uuid4()
OTHER_FOLDER_ID = uuid4()
UNKNOWN_FOLDER_ID = uuid4()
NOTE_ID = uuid4()
OTHER_NOTE_ID = uuid4()
TITLE = "Sample Title"
OTHER_TITLE = "Another Sample Title"
CONTENT = "Sample Content"
OTHER_CONTENT = "Other Content"


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


def test_find_by_user_returns_only_owners_notes(db_session: Session):
    """Repository contract: find_by_user excludes other users' notes."""

    repo = SQLAlchemyNoteRepository(db_session)

    note = Note.create(
        USER_ID, FOLDER_ID, "sample title", "Multi line \n sample content"
    )
    other_note = Note.create(
        OTHER_USER_ID,
        OTHER_FOLDER_ID,
        "other sample title",
        "other Multi line \n sample content",
    )

    repo.save(note)
    repo.save(other_note)

    results = repo.find_by_user(USER_ID)

    result_ids = {n.note_id for n in results}

    assert note.note_id in result_ids
    assert other_note.note_id not in result_ids


def test_find_by_user_excludes_soft_deleted_notes(db_session: Session):
    """Repository contract: find_by_user excludes soft-deleted notes."""

    repo = SQLAlchemyNoteRepository(db_session)

    visible_note = Note.create(
        USER_ID, FOLDER_ID, "sample title", "Multi line \n sample content"
    )
    deleted_note = Note(
        title=Title(TITLE),
        content=Content(CONTENT),
        note_id=NOTE_ID,
        user_id=USER_ID,
        folder_id=FOLDER_ID,
        is_deleted=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_pinned=False,
    )
    repo.save(visible_note)
    repo.save(deleted_note)

    results = repo.find_by_user(USER_ID)
    result_ids = {n.note_id for n in results}

    assert visible_note.note_id in result_ids
    assert deleted_note.note_id not in result_ids


def test_find_by_user_returns_empty_list_when_no_notes(db_session: Session):
    """Repository contract: find_by_user returns [] for a user with no notes."""
    repo = SQLAlchemyNoteRepository(db_session)

    results = repo.find_by_user(USER_ID)
    assert results == []


def test_find_by_user_orders_newest_first(db_session: Session):
    """Repository contract: find_by_user orders results by created_at descending."""
    repo = SQLAlchemyNoteRepository(db_session)

    now = datetime.now(timezone.utc)

    older_note = Note(
        title=Title("Older"),
        content=Content("Older CONTENT"),
        note_id=uuid4(),
        user_id=USER_ID,
        folder_id=FOLDER_ID,
        created_at=now - timedelta(hours=1),
        updated_at=now - timedelta(hours=1),
        is_deleted=False,
        is_pinned=False,
    )
    newer_note = Note(
        title=Title("Newer"),
        content=Content("Newer CONTENT"),
        note_id=uuid4(),
        user_id=USER_ID,
        folder_id=FOLDER_ID,
        created_at=now,
        updated_at=now,
        is_deleted=False,
        is_pinned=False,
    )

    # Save older first, to prove ordering isn't just insertion order.
    repo.save(older_note)
    repo.save(newer_note)

    results = repo.find_by_user(USER_ID)

    assert [n.note_id for n in results] == [newer_note.note_id, older_note.note_id]
