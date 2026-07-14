"""
Tests for the Note aggregate root.

SESSION 3 (Part B) — Note Aggregate
Goal: Note is the aggregate root that owns Title and Content VOs.
      Note.create() is the factory method — the only way to construct new notes.
      Reconstitution (from DB) uses the raw constructor (Session 5).

Cycles:
  [ ] Cycle 20: Note.create() generates unique note_id           → AC-13
  [ ] Cycle 21: Note.create() sets created_at to now             → AC-14
  [ ] Cycle 22: Note.create() sets updated_at == created_at      → AC-15
  [ ] Cycle 23: Note.create() defaults to unpinned, not-deleted  → AC-16
"""
