"""In-memory implementation of FolderRepository (for testing)."""

from uuid import UUID

from app.organization.models import Folder


class InMemoryFolderRepository:

    def __init__(self) -> None:
        self._folders: dict[UUID, Folder] = {}

    def add(self, folder: Folder):
        self._folders[folder.folder_id] = folder

    def find_by_id(self, folder_id: UUID) -> Folder | None:
        return self._folders.get(folder_id)
