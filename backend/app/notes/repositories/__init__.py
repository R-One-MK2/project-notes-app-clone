"""
Public API for Notes Repositories
"""

from app.notes.repositories.in_memory_repo import InMemoryNoteRepository
from app.notes.repositories.ports import NoteRepository

__all__ = ["NoteRepository", "InMemoryNoteRepository"]
