"""Mappers between the Note domain model and NoteORM."""

from app.notes.models.note import Content, Note, Title
from app.notes.repositories.orm import NoteORM


def note_to_orm(note: Note) -> NoteORM:
    """
    Convert domain Note → NoteORM row.

    Used before persistence: domain object goes in, DB-ready row comes out.
    Unwraps Value Objects to raw strings for storage.
    """

    return NoteORM(
        note_id=note.note_id,
        user_id=note.user_id,
        folder_id=note.folder_id,
        title=note.title,
        content=note.content,
        is_pinned=note.is_pinned,
        is_deleted=note.is_deleted,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


def note_from_orm(orm: NoteORM) -> Note:
    """
    Reconstitute domain Note ← NoteORM row.

    Used after retrieval: DB row goes in, rich domain object comes out.
    Wraps raw strings in Value Objects, invoking their validation.
    """

    return Note(
        note_id=orm.note_id,
        user_id=orm.user_id,
        folder_id=orm.folder_id,
        title=Title(orm.title),
        content=Content(orm.content),
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        is_pinned=orm.is_pinned,
        is_deleted=orm.is_deleted,
    )
