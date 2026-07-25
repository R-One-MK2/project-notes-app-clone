"""
Pydantic schemas for the Notes context.

Request and response models used at the HTTP boundary.

Domain rules (title length, content limits) belong in the domain layer's Value Objects, not here.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateNoteIn(BaseModel):
    """Request schema for POST /api/v1/notes."""

    title: str
    folder_id: UUID
    content: str = ""


class NoteDTO(BaseModel):
    """
    Canonical read shape for a note.

    Excludes user_id and is_deleted (info-hiding).
    Used by GET (UC-002), PUT (UC-003), and future list/search endpoints.
    """

    note_id: UUID
    title: str
    content: str
    folder_id: UUID
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
