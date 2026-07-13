"""
Pydantic schemas for the Notes context.

Request and response models used at the HTTP boundary.

Domain rules (title length, content limits) belong in the domain layer's Value Objects, not here.
"""

from uuid import UUID

from pydantic import BaseModel


class CreateNoteIn(BaseModel):
    """Request schema for POST /api/v1/notes."""

    title: str
    folder_id: UUID
    content: str = ""
