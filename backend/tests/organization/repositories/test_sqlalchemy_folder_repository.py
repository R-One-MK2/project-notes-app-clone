"""
Tests for SQLAlchemyFolderRepository (integration with real DB).

SESSION 5 — Persistence Adapters (Folder)
Goal: Verify SQL adapter satisfies the FolderRepository port contract.

Cycles:
  [x] Cycle 41: find_by_id() retrieves saved folder
  [x] Cycle 42: find_by_id() returns None for unknown ID
"""

from uuid import uuid4

from app.organization.models import Folder
from app.organization.repositories import SQLAlchemyFolderRepository
from app.organization.repositories.mappers import folder_to_orm
from sqlalchemy.orm import Session

USER_ID = uuid4()
FOLDER_ID = uuid4()


def test_find_by_id_retrieves_saved_folder(db_session: Session):
    """Contract: find_by_id retrieves what was persisted."""
    repo = SQLAlchemyFolderRepository(db_session)

    folder = Folder(uuid4(), USER_ID)
    db_session.add(folder_to_orm(folder))
    db_session.commit()

    retrieved = repo.find_by_id(folder.folder_id)

    assert retrieved is not None
    assert retrieved.folder_id == folder.folder_id
    assert retrieved.user_id == folder.user_id


def test_find_by_id_returns_none_when_missing(db_session: Session):
    """Contract: unknown ID returns None."""

    repo = SQLAlchemyFolderRepository(db_session)

    result = repo.find_by_id(uuid4())

    assert result is None
