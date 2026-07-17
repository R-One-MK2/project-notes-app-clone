"""Folder entity for the organization context (minimal for UC-01)."""

from uuid import UUID


class Folder:
    """
    A folder that owns notes. Minimal implementation for UC-01.
    Full Folder aggregate (create, rename, delete, nesting) comes in UC-05.
    """

    def __init__(self, folder_id: UUID, user_id: UUID) -> None:
        self._folder_id: UUID = folder_id
        self._user_id: UUID = user_id

    @property
    def folder_id(self) -> UUID:
        return self._folder_id

    @property
    def user_id(self) -> UUID:
        return self._user_id

    def __eq__(self, other: object) -> bool:
        """Entity equality: same folder_id → same folder."""
        if not isinstance(other, Folder):
            return NotImplemented
        return self.folder_id == other.folder_id

    def __hash__(self) -> int:
        return hash(self.folder_id)
