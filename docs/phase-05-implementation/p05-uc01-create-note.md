# UC-001 - Create Note (Email + Password)

> **Use-case specification.** Prose companion to `p5-UC-001-create-note-sequence.puml` / `p5-UC-001-create-note-class.puml`. **Design specification** (code will be source of truth post-implementation).

| Field | Value |
|-------|-------|
| **Use Case ID** | UC-001 |
| **Bounded Context** | «Notes Domain» |
| **Primary Actor** | Authenticated User |
| **Secondary Actors** | - |
| **Type** | User goal |
| **Maturity** | ⚪ Planned · Pre-implementation (Phase 5) |
| **Realises** | FR-002, FR-004, FR-009 · NFR-001, NFR-003 |
| **ADRs** | ADR-001 (Immediate persistence), ADR-002 (Auto-save debounce) |

---

## Description

User creates a new note by entering a title and content, saving it to a folder. The note is immediately persisted to the database (atomic write) and auto-save is enabled for subsequent edits.

This use case *completes* three functional requirements:
- **FR-002:** Create Note (title + content, immediate persistence)
- **FR-004:** Update Note (auto-save on 3-second idle)
- **FR-009:** Note List (new note appears in sidebar)

---

## Preconditions

- User is authenticated (valid JWT token)
- User has at least one folder (default "Notes" folder exists)
- Target folder exists and belongs to the user

---

## Main Flow

1. **User enters note content**
   - User clicks "New Note" button
   - Editor opens with empty title + content fields, assigned to current folder
   - User types title and content

2. **User submits**
   - User clicks "Save" or presses Cmd/Ctrl+S
   - Frontend sends `POST /api/notes {title, content, folder_id}` with JWT

3. **API validates request**
   - Pydantic `CreateNoteRequest` validates body:
     - `title`: required, max 255 chars (VO validation)
     - `content`: optional, max 1MB (VO validation)
     - `folder_id`: required UUID
   - If invalid → `422 Unprocessable Entity`
   - JWT is extracted from `Authorization: Bearer {token}`

4. **Authenticate & authorize**
   - API extracts `user_id` from decoded JWT
   - Passes to `NoteService.create_note(user_id, folder_id, title, content)`

5. **Verify folder ownership**
   - `NoteService` calls `FolderService.get_folder(folder_id)`
   - `FolderService` queries `FolderRepository.find_by_id(folder_id)`
   - Database returns Folder (or null if not found)
   - Service verifies `folder.user_id == user_id` (prevents moving notes to other users' folders)
   - If folder not found or unauthorized → `FolderNotFound` exception → `404 Not Found`

6. **Create Note aggregate**
   - `NoteService` instantiates `Note` domain object:
     ```python
     Note(
       note_id=UUID(),
       user_id=user_id,
       folder_id=folder_id,
       title=Title(title),           # VO: validated + normalised
       content=Content(content),     # VO: validated
       is_pinned=False,
       is_deleted=False,
       created_at=now(),             # Server time
       updated_at=now()
     )
     ```
   - Value objects (`Title`, `Content`) validate during construction
   - If title is empty → ValueError → caught by API → `422 Bad Request`

7. **Persist to database**
   - `NoteService` calls `NoteRepository.save(note)`
   - Repository executes SQL `INSERT INTO notes (...) VALUES (...)`
   - Database guarantees ACID: all columns written atomically or entire INSERT fails
   - If database error (connection lost, constraint violation) → `PersistenceError` → `500 Internal Server Error`

8. **Convert to DTO & return**
   - If success, API converts `Note` → `NoteDTO`:
     ```json
     {
       "note_id": "...",
       "title": "...",
       "content": "...",
       "folder_id": "...",
       "is_pinned": false,
       "created_at": "2026-07-13T02:30:00Z",
       "updated_at": "2026-07-13T02:30:00Z"
     }
     ```
   - Returns `200 OK + NoteDTO`
   - (**Not** included: `user_id`, `is_deleted`, internal timestamps)

9. **Frontend updates**
   - Receives `{note_id, created_at, ...}`
   - Stores `note_id` in editor state (for subsequent edits → `PUT /api/notes/{note_id}`)
   - Shows "Saved" indicator
   - Updates sidebar: new note appears at top of current folder's list

---

## Alternative & Exception Flows

| Scenario | Trigger | Response | Notes |
|----------|---------|----------|-------|
| **Invalid title** | Empty string or > 255 chars | `422 Unprocessable Entity` | Caught by `Title` VO validation during aggregate construction |
| **Invalid content** | > 1 MB | `422 Unprocessable Entity` | Caught by `Content` VO validation |
| **Invalid folder_id** | UUID format error | `422 Unprocessable Entity` | Pydantic rejects malformed UUID |
| **Folder not found** | Folder doesn't exist | `404 Not Found` | `FolderNotFound` exception raised by service |
| **Unauthorized folder** | Folder belongs to different user | `401 Unauthorized` | Service verifies `folder.user_id == user_id` |
| **Database error** | Connection lost, constraint violation | `500 Internal Server Error` | `PersistenceError` translates to HTTP 500 |
| **Expired JWT** | Token past expiry | `401 Unauthorized` | JWT decode fails at API boundary |
| **Malformed JWT** | Invalid signature or structure | `401 Unauthorized` | JWT verification fails |

---

## Postconditions

- Note exists in database with:
  - Unique `note_id` (UUID)
  - Assigned to correct `folder_id` and `user_id`
  - `created_at` and `updated_at` set to server time
  - `is_deleted = false`, `is_pinned = false`
- Note appears in frontend sidebar (current folder's note list)
- Auto-save is enabled: subsequent edits trigger `PUT /api/notes/{note_id}` on 3-second idle (FR-004)
- Note is included in future searches (FR-007) and folder browsing (FR-009)

---

## Implementation Overview

| Layer | File | Responsibility |
|-------|------|-----------------|
| **Frontend** | `app/notes/components/note-editor.tsx` | Editor UI; title/content input; "Save" button handler |
| **Frontend** | `app/notes/api/client.ts` | HTTP client; `POST /api/notes` wrapper |
| **Contract** | `backend/schemas/note_schemas.py` | `CreateNoteRequest`, `NoteDTO` (Pydantic) |
| **API** | `backend/routes/notes.py::create_note` | Endpoint; request validation; error translation to HTTP |
| **API Wiring** | `backend/api/dependencies.py` | `get_note_service`, `get_auth_from_token` (dependency injection) |
| **Application** | `backend/services/note_service.py` | `create_note(user_id, folder_id, title, content)` orchestration |
| **Application** | `backend/services/folder_service.py` | `get_folder(folder_id)` (verify ownership) |
| **Domain** | `backend/models/note.py` | `Note` aggregate root; `created_at`/`updated_at` assignment |
| **Domain** | `backend/models/value_objects.py` | `Title` VO (validates + normalises), `Content` VO (validates) |
| **Persistence** | `backend/repositories/note_repository.py` | `NoteRepository` interface (abstract) |
| **Persistence** | `backend/adapters/sqlalchemy_note_repo.py` | `SQLAlchemy_NoteRepository` implementation; SQL `INSERT` |
| **Persistence** | `backend/adapters/sqlalchemy_folder_repo.py` | `FolderRepository` implementation; folder ownership check |
| **Database** | PostgreSQL | `notes` table (INSERT), `folders` table (SELECT for verification) |

---

## Traceability (Sequence Step → Code)

| Step | What | Code Location |
|------|------|---|
| 1.2 | User submits form | `frontend/app/notes/components/note-editor.tsx::handleSave()` |
| 1.3 | Request validation | `backend/schemas/note_schemas.py::CreateNoteRequest` |
| 1.3' | Invalid body → 422 | FastAPI Pydantic automatic `RequestValidationError` → 422 |
| 2.1 | Extract JWT & authenticate | `backend/api/dependencies.py::get_auth_from_token()` → FastAPI `Depends()` |
| 2.2 | Call service | `backend/routes/notes.py::create_note()::service.create_note(user_id, ...)` |
| 3.1 | Verify folder | `backend/services/note_service.py::NoteService.create_note()` calls `folder_service.get_folder()` |
| 3.2 | Query folder | `backend/repositories/folder_repository.py::find_by_id()` (abstract interface) |
| 3.3 | SQL lookup | `backend/adapters/sqlalchemy_folder_repo.py::find_by_id()` → `SELECT folder WHERE folder_id = ? AND user_id = ?` |
| 3.4 | Folder not found | `backend/services/folder_service.py` → raises `FolderNotFound` → `backend/routes/notes.py` catches as 404 |
| 4.1 | Create Note aggregate | `backend/services/note_service.py::NoteService.create_note()` instantiates `Note(...)` |
| 4.2 | Title validation | `backend/models/value_objects.py::Title.__init__()` validates (required, max 255) |
| 4.3 | Content validation | `backend/models/value_objects.py::Content.__init__()` validates (max 1MB) |
| 5.1 | Persist | `backend/services/note_service.py` calls `note_repo.save(note)` |
| 5.2 | SQL insert | `backend/adapters/sqlalchemy_note_repo.py::save()` → `INSERT INTO notes (...)` |
| 5.3 | Database write | PostgreSQL (atomic transaction) |
| 6.1 | Convert DTO | `backend/routes/notes.py::create_note()` calls `NoteDTO.from_orm(note)` or manual mapping |
| 6.2 | Return 200 | `backend/routes/notes.py::create_note()` → `return NoteDTO(...)` → FastAPI auto-serializes to JSON |
| 7.1 | Update frontend state | `frontend/app/notes/components/note-editor.tsx` receives response, stores `note_id` |
| 7.2 | Show success | Frontend UI shows "Saved" indicator, note appears in list |

---

## Design Decisions & Rationale

### D1: Immediate Persistence (No "Save" Button Delay)
**Decision:** Note is written to database synchronously before returning response (no background queue).

**Rationale:**
- User expects "I saved, it's there" — async writes create lag
- Atomic ACID guarantees prevent partial writes
- Simpler error handling (if save fails, user sees error immediately)

**Trade-off:**
- Slightly slower API response (50ms DB latency vs. 5ms if queued)
- But <200ms total still well within NFR-001 target

**ADR:** ADR-001 (Immediate Persistence for User Trust)

---

### D2: 3-Second Auto-Save Debounce (FR-004)
**Decision:** After user stops typing, wait 3 seconds, then `PUT /api/notes/{note_id}` with new content.

**Rationale:**
- Prevents 1 write per keystroke (network + DB overhead)
- User perceives responsiveness (edits appear instantly in UI)
- 3 seconds is Apple Notes convention (familiar to users)

**Implementation:**
- Frontend debounces input events (debounce library or React hook)
- On `onChange` → clear timeout → set new 3-second timeout
- On timeout expiry → send `PUT /api/notes/{note_id}`
- Show "Saving..." indicator during request, "Saved" on success

**ADR:** ADR-002 (Debounced Auto-Save)

---

### D3: Folder Ownership Verification
**Decision:** Service verifies `folder.user_id == user_id` before creating note.

**Rationale:**
- Prevents horizontal privilege escalation (user A can't create notes in user B's folder)
- Even if folder_id is guessed, authorization fails
- Follows principle of least privilege

**Implementation:**
- `FolderService.get_folder()` does both query AND ownership check
- If unauthorized → `FolderNotFound` (doesn't leak whether folder exists; same error as "not found")

---

### D4: Server-Side Timestamps
**Decision:** `created_at` and `updated_at` are assigned by backend (server time), not client.

**Rationale:**
- Client clocks may be wrong (skewed, timezone issues)
- Server is source of truth for ordering (sort by `updated_at`)
- Prevents time-travel attacks (user backdates notes)

**Implementation:**
- `NoteService` calls Python `datetime.now()` (backend time)
- Frontend never sends timestamps; server assigns them

---

### D5: Value Objects for Title & Content
**Decision:** `Title` and `Content` are domain value objects, not plain strings.

**Rationale:**
- Encapsulates validation (max length, character restrictions)
- Single source of truth for what constitutes valid title/content
- Easier to add rules later (e.g., "no HTML tags") without changing aggregate

**Implementation:**
```python
class Title:
    def __init__(self, value: str):
        if not value or len(value) > 255:
            raise ValueError("Title must be 1-255 chars")
        self.value = value

note = Note(..., title=Title(user_input_title), ...)  # Validates during construction
```

---

### D6: No Rich Text in MVP
**Decision:** Content is plain text only. No bold, italic, lists, etc.

**Rationale:**
- Simplifies implementation (no formatting parser)
- Apple Notes MVP is also plain text (formatting added later)
- Still achieves core goal: take notes

**Future:** Phase 6+ can add `ContentWithFormatting` VO

---

## Known Gaps & Forward Items

1. **Frontend form validation**
   - ⚪ Form UI (empty state, input fields) — needs design
   - ⚪ Client-side validation before sending (pre-check title length)
   - ⚪ Loading spinner during API call

2. **Auto-save implementation**
   - ⚪ Debounce hook (React: `useCallback` + `useEffect` with timeout)
   - ⚪ "Saving..." indicator on `PUT /notes/{note_id}`
   - ⚪ Error handling if save fails (retry? show error banner?)

3. **Error messages**
   - ⚪ Distinguish "folder not found" vs. "unauthorized"? (currently same generic error)
   - ⚪ User-facing error messages (not technical exceptions)

4. **Offline resilience**
   - ⚪ If network fails during create, should frontend queue the request?
   - ⚪ Currently: no offline queue (user loses unsaved work)

5. **Concurrency**
   - ⚪ If user opens same note in 2 tabs and both save, does last-write-win or does one fail?
   - ⚪ Currently: last-write-wins (UTC timestamp comparison)

---

## Related Use Cases

- **UC-002:** Edit Note with Auto-Save (reuses `PUT /api/notes/{note_id}` from step 7)
- **UC-004:** Delete Note (soft delete via `DELETE /api/notes/{note_id}`)
- **UC-006:** Organize Folders (move note between folders)

---

## Deviations from Phase 4 Design (if any, post-implementation)

*To be filled in during Phase 5 coding. List any intentional deviations from modular-design.md signatures.*

---

**Status:** Design complete, ready for Phase 5 implementation.

Signature: Sree (Developer) | Date: July 2026