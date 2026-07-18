from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base


class NoteORM(Base):
    """
    Notes table mapping.

    This is an ORM model — a Python representation of a DB row.
    NOT a domain object. No business logic here.
    """

    __tablename__ = "notes"

    note_id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(index=True)
    folder_id: Mapped[UUID] = mapped_column(index=True)

    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)

    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
