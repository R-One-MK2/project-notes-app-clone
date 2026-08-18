"""
Tests for the NoteService domain orchestration.

SESSION 4 — Domain Service
Goal: NoteService orchestrates authorization + domain creation + persistence.

Cycles:
  [x] Cycle 30: create_note() returns a Note                       → AC-20
  [x] Cycle 31: create_note() persists the note via repository     → AC-19
  [x] Cycle 32: create_note() raises when folder doesn't exist     → AC-17
  [x] Cycle 33: create_note() raises when folder belongs to        → AC-18
                different user
  [x] Cycle 34: created note has correct owner (user_id)           → contract
  [x] Cycle 35: created note has correct folder                    → contract
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from app.notes.models import Content, Note, Title
from app.notes.repositories import InMemoryNoteRepository
from app.notes.services import (
    FolderNotFoundError,
    NoteService,
    UnauthorizedFolderAccessError,
)
from app.notes.services.note_service import NoteNotFoundError
from app.organization.models import Folder
from app.organization.repositories import InMemoryFolderRepository

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


def make_service_with_folder(
    user_id: UUID = USER_ID, other_user_id: UUID | None = None
):
    """
    Helper: build a NoteService with a pre-populated folder.

    The folder belongs to `owner_id` (defaults to USER_ID).
    Tests can pass OTHER_USER_ID to simulate cross-user attempts.
    """
    note_repo = InMemoryNoteRepository()
    folder_repo = InMemoryFolderRepository()

    # Add folder to User
    user_folder = Folder(FOLDER_ID, user_id)
    folder_repo.add(user_folder)

    if other_user_id is not None:
        other_user_folder = Folder(OTHER_FOLDER_ID, other_user_id)
        folder_repo.add(other_user_folder)

    service = NoteService(note_repo, folder_repo)
    return service


def test_create_note_returns_a_note():
    """
    AC-20: create_note returns the created Note aggregate
    """
    service = make_service_with_folder()
    note = service.create_note(USER_ID, FOLDER_ID, TITLE, CONTENT)
    assert isinstance(note, Note)


def test_create_note_persists_via_repository():
    """AC-19: created note is persisted and retrievable."""

    note_repo = InMemoryNoteRepository()
    folder_repo = InMemoryFolderRepository()

    # Add folder to User
    user_folder = Folder(FOLDER_ID, USER_ID)
    folder_repo.add(user_folder)

    note_service = NoteService(note_repo, folder_repo)

    note = note_service.create_note(USER_ID, FOLDER_ID, TITLE, CONTENT)

    assert note is not None

    retrieved = note_repo.find_by_id(note.note_id)

    assert retrieved is not None
    assert retrieved == note


def test_create_note_sets_correct_owner():
    """Contract: created note belongs to the requesting user."""
    note_service = make_service_with_folder(USER_ID)

    note = note_service.create_note(USER_ID, FOLDER_ID, TITLE, CONTENT)

    assert note is not None
    assert note.user_id is not None
    assert USER_ID == note.user_id


def test_create_note_sets_correct_folder():
    """Contract: created note lives in the requested folder."""
    note_service = make_service_with_folder(USER_ID)

    note = note_service.create_note(USER_ID, FOLDER_ID, TITLE, CONTENT)

    assert note is not None
    assert note.folder_id is not None
    assert FOLDER_ID == note.folder_id


# --- Authorization failure tests ---


def test_create_note_raises_when_folder_not_found():
    """AC-17: unknown folder → FolderNotFoundError."""
    note_service = make_service_with_folder()

    with pytest.raises(FolderNotFoundError, match="not found"):
        note_service.create_note(USER_ID, UNKNOWN_FOLDER_ID, TITLE, CONTENT)


def test_create_note_raises_when_folder_belongs_to_different_user():
    """AC-18: folder owned by another user → UnauthorizedFolderAccessError."""
    note_service = make_service_with_folder(OTHER_USER_ID)

    with pytest.raises(UnauthorizedFolderAccessError, match="does not belong to user"):
        note_service.create_note(USER_ID, FOLDER_ID, TITLE, CONTENT)


# ============================================================
# UC-002 Session 1 — get_note()
# ============================================================


def test_get_note_returns_note_when_exists():
    """AC-06: get_note returns the Note aggregate on success."""
    service = make_service_with_folder()

    created = service.create_note(USER_ID, FOLDER_ID, TITLE, CONTENT)
    retrieved = service.get_note(USER_ID, created.note_id)

    assert created == retrieved


def test_get_note_raises_when_missing():
    """AC-07: unknown note_id → NoteNotFoundError."""

    service = make_service_with_folder()

    with pytest.raises(NoteNotFoundError, match="not found"):
        service.get_note(USER_ID, OTHER_NOTE_ID)


def test_get_note_raises_when_wrong_user():
    """AC-08: note owned by another user → NoteNotFoundError (info-hiding)."""
    service = make_service_with_folder(OTHER_USER_ID)

    other_note = service.create_note(OTHER_USER_ID, FOLDER_ID, TITLE, CONTENT)

    with pytest.raises(NoteNotFoundError, match="not found"):
        service.get_note(USER_ID, other_note.note_id)


# ============================================================
# UC-003 Session 2 — update_note()
# ============================================================
def test_list_notes_returns_only_requesting_users_notes():
    """ "
    Tests that the notes only returns the ones belong to the user
    """
    service = make_service_with_folder(other_user_id=OTHER_USER_ID)

    note = service.create_note(USER_ID, FOLDER_ID, TITLE, CONTENT)
    other_note = service.create_note(
        OTHER_USER_ID, OTHER_FOLDER_ID, OTHER_TITLE, OTHER_CONTENT
    )

    notes = service.list_notes(USER_ID)
    assert other_note.note_id not in {note.note_id for note in notes}


def test_excludes_softdeleted_notes():
    """
    Test if soft deleted notes are included in the test
    """
    service = make_service_with_folder()

    # Create visible note
    visible_note = service.create_note(USER_ID, FOLDER_ID, TITLE, CONTENT)

    # Create invisible note and save
    invisible_note = Note(
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
    service._note_repo.save(invisible_note)

    # Call from the repo
    notes = service.list_notes(USER_ID)

    assert visible_note.note_id in {n.note_id for n in notes}
    assert invisible_note.note_id not in {n.note_id for n in notes}


def test_return_empty_list_when_user_has_no_notes():
    """
    Returns empty list when user has no notes
    """
    service = make_service_with_folder()

    notes = service.list_notes(USER_ID)

    assert notes == []


def test_update_note_persists_changes():
    """
    AC-11: update_note mutates the note and persists via repo.
    """

    service = make_service_with_folder()

    note = service.create_note(USER_ID, FOLDER_ID, TITLE, CONTENT)

    updated_note = service.update_note(
        USER_ID, note.note_id, "Updated Title", "Updated Content"
    )

    assert updated_note.title.value == "Updated Title"
    assert updated_note.content.value == "Updated Content"

    retrieved_note = service._note_repo.find_by_id(note.note_id)

    assert retrieved_note is not None
    assert retrieved_note.title.value == "Updated Title"
    assert retrieved_note.content.value == "Updated Content"


def test_update_note_raises_when_note_missing():
    """
    AC-10: unknown note_id → NoteNotFoundError (via get_note).
    """

    service = make_service_with_folder()

    with pytest.raises(NoteNotFoundError, match="not found"):
        service.update_note(USER_ID, NOTE_ID, TITLE, CONTENT)


def test_update_note_raises_when_wrong_user():
    """
    AC-10: note owned by another user → NoteNotFoundError (info-hiding).
    """

    service = make_service_with_folder()

    note = service.create_note(USER_ID, FOLDER_ID, TITLE, CONTENT)
    WRONG_USER_ID = OTHER_USER_ID

    with pytest.raises(NoteNotFoundError, match="not found"):
        service.update_note(
            WRONG_USER_ID, note.note_id, "Updated Title", "Updated Content"
        )
