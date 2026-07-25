"""
Note aggregate root.

The Note is the central domain entity. It owns Title and Content
value objects and enforces invariants at construction AND on mutation.

Two construction entry points:
- Note.create(...): factory for brand-new notes. Generates UUID,
  sets timestamps, applies defaults.
- Note(...): raw constructor for reconstitution from persistence.
  All fields must be provided explicitly.

Mutations (rename, edit_content) delegate validation to the VOs
and bump updated_at while preserving created_at.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.notes.models.value_objects import Content, Title


class Note:
    """Aggregate root for a user's note. Owns Title and Content VOs."""

    def __init__(
        self,
        note_id: UUID,
        user_id: UUID,
        folder_id: UUID,
        title: Title,
        content: Content,
        created_at: datetime,
        updated_at: datetime,
        is_pinned: bool,
        is_deleted: bool,
    ) -> None:
        self._note_id = note_id
        self._user_id = user_id
        self._folder_id = folder_id

        self._title = title
        self._content = content

        self._created_at = created_at
        self._updated_at = updated_at

        self._is_pinned = is_pinned
        self._is_deleted = is_deleted

    @classmethod
    def create(cls, user_id: UUID, folder_id: UUID, title: str, content: str):
        """Factory: create a brand-new note with generated ID and timestamps."""
        now = datetime.now(timezone.utc)
        return cls(
            note_id=uuid4(),
            user_id=user_id,
            folder_id=folder_id,
            title=Title(title),
            content=Content(content),
            created_at=now,
            updated_at=now,
            is_deleted=False,
            is_pinned=False,
        )

    # READ ONLY ACCESSORS
    @property
    def note_id(self) -> UUID:
        return self._note_id

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def folder_id(self) -> UUID:
        return self._folder_id

    @property
    def title(self) -> Title:
        return self._title

    @property
    def content(self) -> Content:
        return self._content

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def is_pinned(self) -> bool:
        return self._is_pinned

    @property
    def is_deleted(self) -> bool:
        return self._is_deleted

    def belongs_to(self, user_id: UUID) -> bool:
        """Domain method: does this note belong to the given user?"""
        return self.user_id == user_id

    def rename(self, new_title: str):
        """
        Replace the title. Delegates validation to Title VO.
        Bumps updated_at; leaves created_at untouched.

        Raises:
            ValueError: if new_title violates Title rules (empty, whitespace, >255).
        """
        self._title = Title(new_title)
        self._updated_at = datetime.now(timezone.utc)

    def edit_content(self, new_content: str):
        """
        Replace the content. Delegates validation to Content VO.

        Raises:
            ValueError: if new_content violates Content rules (>1MB).
        """
        self._content = Content(new_content)
        self._updated_at = datetime.now(timezone.utc)

    # ENTITY EQUALITY
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return NotImplemented
        return self.note_id == other.note_id

    def __hash__(self) -> int:
        return hash(self.note_id)
