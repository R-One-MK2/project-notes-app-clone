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

## Acceptance Criteria

> Single source of truth for verifiable behaviors of the Create Note use case.
> **Traceability chain:** FR → UC → AC → Test → Code → Git commit.
> **Discipline:** Every test cites an AC. Every AC cites an FR. Every commit cites the AC(s) it satisfies.

**Legend:** ⚪ Planned · 🟡 In Progress · 🟢 Verified · 🔴 Failing

#### AC Group 1: HTTP Boundary — Structural Validation

Enforced at the FastAPI/Pydantic layer. Fail-fast before the domain is invoked. Failures result in HTTP 422 (Unprocessable Entity).

| AC ID | Description | Layer | FR / NFR | Test | Session | Status |
|-------|-------------|-------|----------|------|---------|--------|
| AC-01 | Valid, complete request returns HTTP 200 with `{"status": "success"}` | HTTP | FR-002 | `test_valid_request_returns_success` | 2 | 🟡 |
| AC-02 | Request missing `title` field returns 422 | HTTP (Pydantic) | FR-002 | `test_missing_title_returns_422` | 2 | 🟡 |
| AC-03 | Request with non-string `title` returns 422 | HTTP (Pydantic) | FR-002 | `test_title_wrong_type_returns_422` | 2 | 🟡 |
| AC-04 | Request missing `folder_id` field returns 422 | HTTP (Pydantic) | FR-002 | `test_missing_folder_id_returns_422` | 2 | 🟡 |
| AC-05 | Request with malformed UUID `folder_id` returns 422 | HTTP (Pydantic) | FR-002 | `test_invalid_folder_id_returns_422` | 2 | 🟡 |
| AC-06 | Request missing `content` is accepted (content is optional, defaults to empty) | HTTP (Pydantic) | FR-002 | `test_missing_content_is_optional` | 2 | 🟡 |

#### AC Group 2: Domain — Business Rule Validation

Enforced inside the domain (Value Objects and Domain Services). They protect the domain regardless of how data arrives (HTTP, CLI, tests).

| AC ID | Description | Layer | FR / NFR | Test | Session | Status |
|-------|-------------|-------|----------|------|---------|--------|
| AC-07 | Empty string title is rejected | Domain (Title VO) | FR-002 | `test_title_empty_raises` | 3 | ⚪ |
| AC-08 | Whitespace-only title is rejected | Domain (Title VO) | FR-002 | `test_title_whitespace_only_raises` | 3 | ⚪ |
| AC-09 | Title over 255 characters is rejected | Domain (Title VO) | FR-002 | `test_title_too_long_raises` | 3 | ⚪ |
| AC-10 | Title with leading/trailing whitespace is stripped | Domain (Title VO) | FR-002 | `test_title_strips_whitespace` | 3 | ⚪ |
| AC-11 | Content over 1 MB is rejected | Domain (Content VO) | FR-002 | `test_content_too_large_raises` | 3 | ⚪ |
| AC-12 | Empty content is allowed | Domain (Content VO) | FR-002 | `test_content_empty_allowed` | 3 | ⚪ |

#### AC Group 3: Domain — Aggregate Invariants

Govern how the `Note` aggregate is constructed and behaves.

| AC ID | Description | Layer | FR / NFR | Test | Session | Status |
|-------|-------------|-------|----------|------|---------|--------|
| AC-13 | Note is created with a fresh UUID (uniqueness) | Domain (Note.create) | FR-002 | `test_note_create_generates_unique_id` | 3 | ⚪ |
| AC-14 | Note has server-generated `created_at` timestamp | Domain (Note.create) | FR-002 | `test_note_create_sets_created_at` | 3 | ⚪ |
| AC-15 | Note has server-generated `updated_at` timestamp equal to `created_at` on creation | Domain (Note.create) | FR-002 | `test_note_create_sets_updated_at_equal_to_created_at` | 3 | ⚪ |
| AC-16 | New note defaults to `is_pinned=False` and `is_deleted=False` | Domain (Note.create) | FR-002 | `test_note_create_defaults` | 3 | ⚪ |

#### AC Group 4: Domain Service — Business Logic

Enforced by `NoteService.create_note()`, which orchestrates the domain logic.

| AC ID | Description | Layer | FR / NFR | Test | Session | Status |
|-------|-------------|-------|----------|------|---------|--------|
| AC-17 | Service verifies the target folder exists | Domain (NoteService) | FR-002, FR-006 | `test_create_note_folder_must_exist` | 4 | ⚪ |
| AC-18 | Service verifies the target folder belongs to the requesting user (authorization) | Domain (NoteService) | FR-002, NFR-002 | `test_create_note_folder_must_belong_to_user` | 4 | ⚪ |
| AC-19 | Service persists the note via `NoteRepository.save()` | Domain (NoteService) | FR-002 | `test_create_note_persists_via_repository` | 4 | ⚪ |
| AC-20 | Service returns the created Note aggregate | Domain (NoteService) | FR-002 | `test_create_note_returns_note` | 4 | ⚪ |

#### AC Group 5: Persistence — Adapter Behavior

Verify the SQLAlchemy repository correctly translates between the domain and the database.

| AC ID | Description | Layer | FR / NFR | Test | Session | Status |
|-------|-------------|-------|----------|------|---------|--------|
| AC-21 | Repository writes note to `notes` table via ACID transaction | Infrastructure | FR-002, NFR-001 | `test_note_repository_saves_to_db` | 5 | ⚪ |
| AC-22 | Repository can retrieve the saved note by ID | Infrastructure | FR-002 | `test_note_repository_finds_by_id` | 5 | ⚪ |
| AC-23 | Repository preserves title and content values exactly | Infrastructure | FR-002 | `test_note_repository_preserves_values` | 5 | ⚪ |
| AC-24 | Repository failures propagate as domain-safe exceptions | Infrastructure | NFR-001 | `test_note_repository_db_error_raises` | 5 | ⚪ |

#### AC Group 6: Authentication & Authorization

Verify JWT-based authentication and authorization at the HTTP boundary.

| AC ID | Description | Layer | FR / NFR | Test | Session | Status |
|-------|-------------|-------|----------|------|---------|--------|
| AC-25 | Request without `Authorization` header returns 401 | HTTP (Auth Dependency) | FR-001, NFR-002 | `test_missing_auth_returns_401` | 6 | ⚪ |
| AC-26 | Request with invalid JWT returns 401 | HTTP (Auth Dependency) | FR-001, NFR-002 | `test_invalid_jwt_returns_401` | 6 | ⚪ |
| AC-27 | Request with expired JWT returns 401 | HTTP (Auth Dependency) | FR-001, NFR-002 | `test_expired_jwt_returns_401` | 6 | ⚪ |
| AC-28 | `user_id` is extracted from JWT `sub` claim, never from request body | HTTP (Auth Dependency) | FR-001, NFR-002 | `test_user_id_from_jwt_not_body` | 6 | ⚪ |
| AC-29 | Cross-user folder access returns 404 (info-hiding — does not reveal existence) | Domain + HTTP | NFR-002 | `test_other_users_folder_returns_404` | 6 | ⚪ |

#### AC Group 7: Response Contract

Define what the client receives when creation succeeds.

| AC ID | Description | Layer | FR / NFR | Test | Session | Status |
|-------|-------------|-------|----------|------|---------|--------|
| AC-30 | Successful creation returns HTTP 201 (Created), not 200 | HTTP | FR-002 | `test_create_note_returns_201` | 7 | ⚪ |
| AC-31 | Response body is a `NoteDTO` containing `note_id`, `title`, `content`, `folder_id`, `is_pinned`, `created_at`, `updated_at` | HTTP (DTO) | FR-002 | `test_response_matches_note_dto` | 7 | ⚪ |
| AC-32 | Response never exposes `user_id` or `is_deleted` (information hiding) | HTTP (DTO) | NFR-002 | `test_response_hides_internal_fields` | 7 | ⚪ |

#### AC Group 8: Observability

Verify the endpoint is observable in production.

| AC ID | Description | Layer | FR / NFR | Test | Session | Status |
|-------|-------------|-------|----------|------|---------|--------|
| AC-33 | Every POST is logged at INFO level | Middleware/Route | NFR-005 | `test_post_notes_logs_at_info_level` | 1 | 🟢 |
| AC-34 | Log message includes HTTP method and path | Middleware/Route | NFR-005 | `test_post_notes_log_includes_method_and_path` | 1 | 🟢 |
| AC-35 | Failed requests (4xx, 5xx) are logged with appropriate severity | Middleware/Route | NFR-005 | `test_failed_requests_are_logged` | 6 | ⚪ |

#### AC Group 9: End-to-End (Integration)

Verify the full stack, with a real database.

| AC ID | Description | Layer | FR / NFR | Test | Session | Status |
|-------|-------------|-------|----------|------|---------|--------|
| AC-36 | Full flow: authenticated request → 201 → note persisted in DB → retrievable via GET | E2E | FR-002 | `test_e2e_create_and_retrieve_note` | 8 | ⚪ |
| AC-37 | Concurrent creates by same user do not corrupt state | E2E | NFR-001 | `test_e2e_concurrent_creates` | 8 | ⚪ |

#### AC Summary Statistics

| Session | AC Count | Status |
|---------|----------|--------|
| Session 1: HTTP plumbing | 2 (AC-33, AC-34) | 🟢 Complete |
| Session 2: Request validation | 6 (AC-01 to AC-06) | 🟡 In Progress |
| Session 3: Domain (VOs + Note aggregate) | 10 (AC-07 to AC-16) | ⚪ Planned |
| Session 4: Domain service | 4 (AC-17 to AC-20) | ⚪ Planned |
| Session 5: Persistence adapter | 4 (AC-21 to AC-24) | ⚪ Planned |
| Session 6: Auth + authorization | 5 (AC-25 to AC-29) | ⚪ Planned |
| Session 7: Response contract | 3 (AC-30 to AC-32) | ⚪ Planned |
| Session 8: E2E integration | 2 (AC-36, AC-37) | ⚪ Planned |
| Observability (spans sessions) | 1 (AC-35) | ⚪ Planned |
| **Total for UC-01** | **37** | 2/37 (5%) |

#### AC Usage Rules

1. **Never write a test without an AC.** If you can't cite `AC-NN`, don't write the test — add the AC to this doc first.
2. **Every AC must have exactly one test.** If a behavior needs two tests, split it into two ACs.
3. **Update status as you go.** Start of cycle → 🟡 In Progress. Test passes green → 🟢 Verified. Test breaks → 🔴 Failing (fix immediately).
4. **Commit messages cite AC IDs.** Example: `FEATURE-UC01-CREATE-NOTE: [AC-02, AC-03] request validation for title`
5. **Deviations must be documented.** If an AC turns out to be wrong or infeasible, update this doc with a note explaining why, before removing/changing the AC.

#### AC Deviations & Notes

*None yet. Add entries as they arise during implementation.*

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