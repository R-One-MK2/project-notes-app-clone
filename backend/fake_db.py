from uuid import uuid4

from app.notes.models import Note
from app.notes.repositories import NoteRepository


class FakeQuickNote:

    def __init__(self) -> None:
        self.saved = []

    def save(self, note: Note):
        self.saved.append(note)

    def find_by_id(self, note_id):
        for note in self.saved:
            if note.note_id == note_id:
                return note
        return None


def demo_persistence(repo: NoteRepository):
    note = Note.create(uuid4(), uuid4(), "Test", "Content")
    repo.save(note)
    retrieved = repo.find_by_id(note.note_id)
    print(f"Saved and retrieved: {retrieved == note}")


if __name__ == "__main__":
    demo_persistence(FakeQuickNote())
