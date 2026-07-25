import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_session
from app.notes.repositories import SQLAlchemyNoteRepository
from app.notes.schemas import CreateNoteIn
from app.notes.services import NoteService
from app.notes.services.note_service import (
    FolderNotFoundError,
    UnauthorizedFolderAccessError,
)
from app.organization.repositories import SQLAlchemyFolderRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


# Placeholder until Session 6 (auth) replaces with real JWT-extracted user_id
def get_current_user_id() -> UUID:
    """Return a fixed user_id for development. Replaced in Session 6."""
    return UUID("00000000-0000-0000-0000-000000000001")


def get_note_service(session: Session = Depends(get_session)) -> NoteService:
    return NoteService(
        note_repo=SQLAlchemyNoteRepository(session),
        folder_repo=SQLAlchemyFolderRepository(session),
    )


@router.post("")
def create_note(
    request: CreateNoteIn,
    service: NoteService = Depends(get_note_service),
    user_id: UUID = Depends(get_current_user_id),
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
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedFolderAccessError as e:
        logger.warning("Unauthorized folder access: %s", e)
        # Info-hiding: same status as not found (attackers can't enumerate folders)
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"status": "success", "note_id": str(note.note_id)}
