"""Mappers between Folder domain model and FolderORM."""

from app.organization.models import Folder
from app.organization.repositories.orm import FolderORM


def folder_to_orm(folder: Folder) -> FolderORM:
    """Convert domain Folder → FolderORM row for persistence."""
    return FolderORM(folder_id=folder.folder_id, user_id=folder.user_id)


def folder_from_orm(orm: FolderORM) -> Folder:
    """Reconstitute domain Folder ← FolderORM row."""
    return Folder(folder_id=orm.folder_id, user_id=orm.user_id)
