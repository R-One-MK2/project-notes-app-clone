"""Domain service for the Notes bounded context."""

from __future__ import annotations

from uuid import UUID

from app.notes.models import Note
from app.notes.repositories import NoteRepository
from app.organization.repositories import FolderRepository


class FolderNotFoundError(Exception):
    """Raised when the target folder does not exist."""


class UnauthorizedFolderAccessError(Exception):
    """Raised when the folder exists but does not belong to the user."""


class NoteNotFoundError(Exception):
    """
    Raised when a note cannot be retrieved.

    Used uniformly for three distinct cases (info-hiding):
    - Note doesn't exist
    - Note belongs to a different user
    - Note is soft-deleted
    """


class NoteService:
    """
    Orchestrates note-related business logic.

    Cross-aggregate concerns (folder authorization + persistence) live here.
    Single-aggregate rules (title/content validation) live in Note/Title/Content.
    """

    def __init__(
        self, note_repo: NoteRepository, folder_repo: FolderRepository
    ) -> None:
        self._note_repo = note_repo
        self._folder_repo = folder_repo

    def create_note(
        self, user_id: UUID, folder_id: UUID, title: str, content: str
    ) -> Note:
        """
        Create a new note in the given folder.

        Raises:
            FolderNotFoundError: if the folder does not exist.
            UnauthorizedFolderAccessError: if the folder belongs to another user.
            ValueError: if title/content violate domain rules (raised by VOs).
        """

        # Check if the folder exist in database
        folder = self._folder_repo.find_by_id(folder_id)

        # Raise error if it does
        if folder is None:
            raise FolderNotFoundError(f"Folder {folder_id} not found")

        # Raise if it belong to another user
        if not folder.belongs_to(user_id):
            raise UnauthorizedFolderAccessError(
                f"Folder {folder_id} does not belong to user {user_id}"
            )
        # Create Note
        note = Note.create(user_id, folder_id, title, content)

        # persist the note
        self._note_repo.save(note)
        return note

    def get_note(self, user_id: UUID, note_id: UUID) -> Note:
        """
        Retrieve a note by ID, enforcing ownership and non-deletion.

        Raises:
            NoteNotFoundError: if the note doesn't exist, belongs to
                another user, or is soft-deleted. Same exception across
                all three cases for info-hiding.
        """

        note = self._note_repo.find_by_id(note_id)

        if note is None:
            raise NoteNotFoundError(f"Note {note_id} not found!")

        if note.user_id != user_id:
            raise NoteNotFoundError(f"Note {note_id} not found!")

        if note.is_deleted:
            raise NoteNotFoundError(f"Note {note_id} not found!")

        return note

    def update_note(
        self, user_id: UUID, note_id: UUID, title: str, content: str
    ) -> Note:
        """
        Update a note's title and content.

        Reuses get_note() for authorization (missing/wrong user/deleted → 404).
        Delegates validation to Title/Content VOs via aggregate mutators.

        Raises:
            NoteNotFoundError: if note doesn't exist, belongs to another user,
                or is soft-deleted.
            ValueError: if title/content violate domain rules (from VOs).
        """
        note = self.get_note(user_id, note_id)

        # Update the Contents
        note.rename(title)
        note.edit_content(content)

        # Persist Note
        self._note_repo.save(note)

        # Return Note
        return note
