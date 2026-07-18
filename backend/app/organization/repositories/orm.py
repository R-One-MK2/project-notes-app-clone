"""SQLAlchemy ORM models for the Organization context."""

from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class FolderORM(Base):
    """
    Folders table mapping.

    Minimal for UC-01 authorization checks. Full folder schema in UC-05.
    """

    __tablename__ = "folders"

    folder_id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(index=True)
