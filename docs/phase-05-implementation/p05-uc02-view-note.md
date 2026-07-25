# UC-02: View Note

**Goal:** User opens an existing note; full content + metadata load into the editor.
**Realises:** FR-003
**Depends on:** UC-01 (existing notes to view)
**Auth:** Deferred to horizontal slice — routes use placeholder `get_current_user_id` for now.

---

## Endpoints

```
GET  /api/v1/notes/{note_id}    → 200 NoteDTO | 404 | 422
```

---

## Acceptance Criteria

**Legend:** ⚪ Planned · 🟡 In Progress · 🟢 Verified

### HTTP layer

| AC | Description | Status |
|----|------|--------|
| AC-01 | GET existing note returns 200 + `NoteDTO` | ⚪ |
| AC-02 | GET missing note returns 404 | ⚪ |
| AC-03 | GET with malformed UUID returns 422 | ⚪ |

### Service layer

| AC | Description | Status |
|----|------|--------|
| AC-04 | `get_note` raises `NoteNotFoundError` if note missing OR wrong user OR deleted | ⚪ |

**Total: 4 ACs.** Implemented alongside UC-03 (shared sessions — see the UC-03 session plan).

---

## Design Decisions

### D1: Info-hiding on all lookups
Not-found, unauthorized, and deleted all return 404. Same reasoning as UC-01 (folder authorization).

### D2: Trash notes are not viewable
Soft-deleted notes return 404 on GET. Matches Apple Notes UX (restore from Trash first); enforced at the domain layer so it holds for any future entry point.

---

## Related Use Cases

- **UC-01 Create Note** — established the shape UC-02 reads
- **UC-03 Edit Note** — viewing is the precondition for editing; shares `get_note` and the DTO
- **UC-04 Search Note** — search results open into this view
- **UC-05 Delete Note (soft delete)** — sets `is_deleted = true`; UC-02 rejects such notes
