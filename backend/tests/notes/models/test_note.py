"""
Tests for the Note aggregate root.

SESSION 3 (Part B) — Note Aggregate
Goal: Note is the aggregate root that owns Title and Content VOs.
      Note.create() is the factory method — the only way to construct new notes.
      Reconstitution (from DB) uses the raw constructor (Session 5).

Cycles:
  [x] Cycle 20: Note.create() generates unique note_id           → AC-13
  [x] Cycle 21: Note.create() sets created_at to now             → AC-14
  [x] Cycle 22: Note.create() sets updated_at == created_at      → AC-15
  [ ] Cycle 23: Note.create() defaults to unpinned, not-deleted  → AC-16
"""

# Test fixtures — reusable valid inputs
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from app.notes.models import Content, Note, Title

# from app.notes.models.note import Note
# from app.notes.models.value_objects import Content, Title

USER_ID = uuid4()
FOLDER_ID = uuid4()
VALID_TITLE = Title("Grocery List")
VALID_CONTENT = Content("Milk, Eggs, Bread")


def test_note_create_generates_unique_note_id():
    """
    AC-13: Note.create() generates a fresh UUID for each note.

    Two notes created back-to-back must have different IDs.
    Requirement: FR-002 — each note has a unique identifier.
    """
    note1 = Note.create(USER_ID, FOLDER_ID, VALID_TITLE, VALID_CONTENT)
    note2 = Note.create(USER_ID, FOLDER_ID, VALID_TITLE, VALID_CONTENT)

    assert isinstance(note1.note_id, UUID)
    assert isinstance(note2.note_id, UUID)
    assert note1.note_id != note2.note_id


def test_note_create_generates_sets_created_at_to_now():
    """
    AC-14: Note.create() sets created_at to the current time.

    The timestamp is server-generated, not client-provided.
    Requirement: FR-002 — creation time recorded automatically.
    """
    before = datetime.now()
    note = Note.create(USER_ID, FOLDER_ID, VALID_TITLE, VALID_CONTENT)
    after = datetime.now()

    assert isinstance(note.created_at, datetime)
    assert before <= note.created_at <= after


def test_note_create_sets_updated_at_equal_equal_to_created_at():
    """
    AC-15: Note.create() sets updated_at equal to created_at.

    On creation, a note has never been updated, so both timestamps
    are the same moment. Later edits will diverge them.
    Requirement: FR-002 — updated_at initialized on creation.
    """

    note = Note.create(USER_ID, FOLDER_ID, VALID_TITLE, VALID_CONTENT)

    assert note.created_at == note.updated_at


def test_note_crate_defaults_to_unpinned_and_not_deleted():
    """
    AC-16: Note.create() defaults to is_pinned=False, is_deleted=False.

    New notes are visible in the folder and not pinned.
    Requirement: FR-002 — sensible defaults on creation.
    """
    note = Note.create(USER_ID, FOLDER_ID, VALID_TITLE, VALID_CONTENT)

    assert note.is_deleted is False
    assert note.is_pinned is False


def test_note_create_wraps_strings_in_value_objects():
    """
    Note contract: title and content are wrapped in VOs internally.

    The factory accepts raw strings for convenience but converts
    them to Title and Content VOs, ensuring domain rules apply.
    """

    note = Note.create(USER_ID, FOLDER_ID, VALID_TITLE, VALID_CONTENT)

    assert isinstance(note.title, Title)
    assert isinstance(note.content, Content)

    assert note.title.value == VALID_TITLE.value
    assert note.content.value == VALID_CONTENT.value


def test_notes_with_same_id_are_equal():
    """
    Note is an ENTITY — equality is based on identity (note_id),
    not attributes. Two notes with the same ID are the same note
    (perhaps in different states).
    """
    note_original = Note.create(USER_ID, FOLDER_ID, VALID_TITLE, VALID_CONTENT)
    note_updated = Note(
        note_id=note_original.note_id,
        user_id=note_original.user_id,
        folder_id=note_original.folder_id,
        title=Title("Updated Title"),
        content=Content("Updated Content"),
        created_at=note_original.created_at,
        updated_at=note_original.updated_at + timedelta(hours=1),
        is_pinned=True,
        is_deleted=False,
    )

    assert note_original == note_updated
