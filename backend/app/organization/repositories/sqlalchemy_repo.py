"""SQLAlchemy adapter for FolderRepository port."""

from uuid import UUID

from app.organization.models import Folder
from app.organization.repositories.mappers import folder_from_orm
from app.organization.repositories.orm import FolderORM


class SQLAlchemyFolderRepository:
    """
    Real FolderRepository backed by SQLAlchemy.

    Satisfies the FolderRepository port. UC-01 only needs find_by_id.
    """

    def __init__(self, session) -> None:
        self._session = session

    def find_by_id(self, folder_id: UUID) -> Folder | None:
        """Retrieve folder by primary key. Returns None if not found."""
        orm = self._session.get(FolderORM, folder_id)
        if orm is None:
            return None
        return folder_from_orm(orm)
