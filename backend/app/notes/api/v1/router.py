import logging

from fastapi import APIRouter

from app.notes.schemas import CreateNoteIn

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


@router.post("")
def create_note(req: CreateNoteIn) -> dict:
    """
    Create a new note.
    Currently a stub — returns success without persisting anything.
    Future sessions will add request validation, domain logic, and persistence.
    """
    logger.info("POST /api/v1/notes")
    return {"status": "success"}
