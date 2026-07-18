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

from uuid import UUID, uuid4

import pytest
from app.notes.models import Note
from app.notes.repositories import InMemoryNoteRepository
from app.notes.services import (
    FolderNotFoundError,
    NoteService,
    UnauthorizedFolderAccessError,
)
from app.organization.models import Folder
from app.organization.repositories import InMemoryFolderRepository

USER_ID = uuid4()
OTHER_USER_ID = uuid4()
FOLDER_ID = uuid4()
UNKNOWN_FOLDER_ID = uuid4()
NOTE_ID = uuid4()
TITLE = "Sample Title"
CONTENT = "Sample Content"


def make_service_with_folder(user_id: UUID = USER_ID):
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
