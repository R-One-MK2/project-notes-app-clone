from typing import Protocol
from uuid import UUID

from app.organization.models import Folder


class FolderRepository(Protocol):
    """
    Port: interface any folder repository must implement.

    Adapters:
    - InMemoryFolderRepository (Session 4, for testing)
    - SQLAlchemyFolderRepository (Session 5, for production)
    """

    def find_by_id(self, folder_id: UUID) -> Folder | None:
        """Retrieve a folder by ID. Returns None if not found."""
        ...
