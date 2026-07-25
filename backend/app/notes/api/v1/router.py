import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_session
from app.notes.repositories import SQLAlchemyNoteRepository
from app.notes.schemas import CreateNoteIn, NoteDTO
from app.notes.services import NoteService
from app.notes.services.note_service import (
    FolderNotFoundError,
    NoteNotFoundError,
    UnauthorizedFolderAccessError,
)
from app.organization.repositories import SQLAlchemyFolderRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


# Placeholder until Session 6 (auth) replaces with real JWT-extracted user_id
def get_current_user_id() -> UUID:
    """Return a fixed user_id for development. Replaced in Session 6."""
    return UUID("00000000-0000-0000-0000-000000000001")


def get_note_service(session: Annotated[Session, Depends(get_session)]) -> NoteService:
    return NoteService(
        note_repo=SQLAlchemyNoteRepository(session),
        folder_repo=SQLAlchemyFolderRepository(session),
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"description": "Folder not found or not owned by user"},
    },
)
def create_note(
    request: CreateNoteIn,
    service: Annotated[NoteService, Depends(get_note_service)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict:
    """
    Create a new note.
    Currently a stub — returns success without persisting anything.
    Future sessions will add request validation, domain logic, and persistence.
    """
    logger.info("POST /api/v1/notes")

    try:
        note = service.create_note(
            user_id=user_id,
            folder_id=request.folder_id,
            title=request.title,
            content=request.content,
        )
    except FolderNotFoundError as e:
        logger.warning("Folder not found: %s", e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )
    except UnauthorizedFolderAccessError as e:
        logger.warning("Unauthorized folder access: %s", e)
        # Info-hiding: same status as not found (attackers can't enumerate folders)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )
    return {"status": "success", "note_id": str(note.note_id)}


@router.get(
    "/{note_id}",
    responses={
        404: {"description": "Note not found or not owned by user"},
    },
)
def get_note(
    note_id: UUID,
    service: Annotated[NoteService, Depends(get_note_service)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> NoteDTO:
    """
    Retrieve a note by ID.

    Returns 404 if the note doesn't exist, belongs to another user,
    or is soft-deleted (info-hiding).
    """
    logger.info("GET /api/v1/notes/%s", note_id)

    try:
        note = service.get_note(user_id=user_id, note_id=note_id)
    except NoteNotFoundError as e:
        logger.warning("Note not found: %s", e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )

    return NoteDTO(
        note_id=note.note_id,
        title=note.title.value,
        content=note.content.value,
        folder_id=note.folder_id,
        is_pinned=note.is_pinned,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )
