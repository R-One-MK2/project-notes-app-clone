"""
Tests for the in-memory folder repository.

SESSION 4 — Repository Adapters (Part A: Folder)
Goal: Fake FolderRepository for testing service authorization checks.

Cycles:
  [x] Cycle 28: find_by_id() returns folder if exists
  [] Cycle 29: find_by_id() returns None if not exists
"""

from uuid import uuid4

from app.organization.models import Folder
from app.organization.repositories import InMemoryFolderRepository


def test_find_by_id_return_folder_if_exists():
    """
    Repository contract: find_by_id returns the stored folder
    """

    repo = InMemoryFolderRepository()
    user_id = uuid4()
    folder_id = uuid4()
    folder = Folder(folder_id, user_id)
    repo.add(folder)

    result = repo.find_by_id(folder_id)

    assert result is not None
    assert result.folder_id == folder_id
    assert result._user_id == user_id
