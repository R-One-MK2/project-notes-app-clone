# UC-002: View Note

> **Use case specification.** Prose companion to `p05-uc002-view-note-sequence.puml` and `p05-uc002-view-note-class.puml`.

| Field | Value |
|-------|-------|
| **Use Case ID** | UC-002 |
| **Bounded Context** | «Notes Domain» |
| **Primary Actor** | Authenticated User |
| **Type** | User goal |
| **Maturity** | ⚪ Planned — Pre-implementation |
| **Realises** | FR-003 |
| **Depends On** | UC-001 (notes must exist to view) |
| **Unblocks** | UC-003 (Edit Note requires a viewable note first) |

---

## Description

The user retrieves a single note by ID. The response is a `NoteDTO` containing the note's public fields; internal fields (`user_id`, `is_deleted`) are never exposed. The endpoint applies **information hiding** on all failure modes — missing notes, notes owned by other users, and soft-deleted notes all return `404 Not Found` with an identical error body.

**Auth is deferred to a horizontal slice.** A placeholder `get_current_user_id()` returns a fixed UUID during MVP development. Real JWT extraction will land later without touching UC-002 code.

---

## Endpoint

```
GET /api/v1/notes/{note_id}
```

**Success:** `200 OK` + `NoteDTO`
**Failure:** `404 Not Found` (missing, unauthorized, deleted) | `422 Unprocessable Entity` (malformed UUID)

---

## Acceptance Criteria

> Every test cites an AC. Every AC cites a functional requirement. Every commit cites the AC(s) it satisfies.

**Legend:** ⚪ Planned · 🟡 In Progress · 🟢 Verified · 🔴 Failing

### AC Group 1 — HTTP boundary

Enforced by FastAPI + Pydantic. Failures return `422` before the domain is invoked.

| AC | Description | FR | Test | Session | Status |
|----|------|----|------|---------|--------|
| AC-01 | GET existing note returns `200 OK` + `NoteDTO` | FR-003 | `test_get_note_returns_200_with_dto` | S2 | ⚪ |
| AC-02 | GET with malformed UUID `note_id` returns `422` | FR-003 | `test_get_note_malformed_uuid_returns_422` | S2 | ⚪ |
| AC-03 | GET for nonexistent note returns `404` | FR-003 | `test_get_missing_note_returns_404` | S2 | ⚪ |
| AC-04 | Response body matches `NoteDTO` shape (all seven public fields present) | FR-003 | `test_get_note_response_shape` | S2 | ⚪ |
| AC-05 | Response never exposes `user_id` or `is_deleted` | NFR-002 | `test_get_note_hides_internal_fields` | S2 | ⚪ |

### AC Group 2 — Service layer

Enforced by `NoteService.get_note()`. Same info-hiding logic across all failure modes.

| AC | Description | FR | Test | Session | Status |
|----|------|----|------|---------|--------|
| AC-06 | `get_note(user_id, note_id)` returns the `Note` aggregate on success | FR-003 | `test_get_note_returns_note` | S1 | ⚪ |
| AC-07 | `get_note` raises `NoteNotFoundError` when note doesn't exist | FR-003 | `test_get_note_missing_raises` | S1 | ⚪ |
| AC-08 | `get_note` raises `NoteNotFoundError` when note belongs to another user (info-hiding) | NFR-002 | `test_get_note_other_user_raises_not_found` | S1 | ⚪ |

**Total: 8 ACs across 2 sessions.**

---

## Sessions

| Session | Scope | ACs | Est. |
|---------|-------|------|------|
| **S1** | Add `get_note()` service method + `NoteNotFoundError` + service tests (in-memory repo) | AC-06 to AC-08 | 1.5h |
| **S2** | Add `NoteDTO` schema + GET route + response mapping + E2E test (SQL repo) | AC-01 to AC-05 | 1.5h |

**Total: ~3 hours across 1–2 sittings.**

---

## Design Decisions

### D1 — Introduce `NoteDTO` as canonical read shape

**Decision:** UC-002 introduces a Pydantic `NoteDTO` for all note-read responses. This DTO will be reused by UC-003 (Edit) and all future read endpoints (list, search).

**Rationale:**
- UC-001's response (`{"status": "success", "note_id": ...}`) was a creation acknowledgement, not a canonical note representation
- Every read endpoint needs a consistent shape; introducing it now avoids per-endpoint drift
- Pydantic serialization gives us JSON conversion for free (`datetime` → ISO strings, `UUID` → strings)

**Fields exposed:** `note_id`, `title`, `content`, `folder_id`, `is_pinned`, `created_at`, `updated_at`
**Fields hidden:** `user_id`, `is_deleted`

### D2 — Info-hiding on all lookup failures

**Decision:** Missing note, wrong-user note, and soft-deleted note all return `404 Not Found` with identical response body. The client cannot distinguish between the three cases.

**Rationale:**
- Attackers must not be able to enumerate valid note IDs across users
- Different error codes leak information ("this ID exists but not yours")
- Same pattern as UC-001's folder-authorization behavior — architectural consistency
- Cost is trivial: legitimate users rarely encounter this path

### D3 — Auth deferred to horizontal slice

**Decision:** UC-002 continues to use the placeholder `get_current_user_id()` from UC-001. Real JWT extraction is deferred to a horizontal slice that will replace the placeholder uniformly across all UCs.

**Rationale:**
- Vertical slicing (delivering complete features) matters more than horizontal completeness (auth everywhere)
- Auth-gating every endpoint from day one delays user-visible functionality
- The route/service layer accepts a `user_id` parameter; only the *source* of that value changes when auth lands

### D4 — Soft-deleted notes are hidden from view

**Decision:** If `note.is_deleted == True`, GET returns `404`. Trashed notes are invisible until UC-005 (Restore) reactivates them.

**Rationale:**
- Matches Apple Notes UX: trashed notes disappear from normal folder views
- Enforced at the domain layer (`NoteService.get_note`) so the rule holds regardless of entry point (future CLI, future GraphQL, etc.)
- Deferred detail: soft-delete flag isn't set anywhere yet (UC-004 hasn't been built), so this check is theoretical for MVP — but the guard is cheap to add now and correct forever

---

## Preconditions

- Note exists in the database (created via UC-001)
- Note belongs to the requesting user
- Note is not soft-deleted (`is_deleted == false`)

---

## Main Flow

1. User requests a specific note via `GET /api/v1/notes/{note_id}`
2. FastAPI parses the path parameter as a `UUID` (invalid format → 422)
3. Route resolves dependencies: DB session, placeholder `user_id`, `NoteService` instance
4. Route calls `service.get_note(user_id, note_id)`
5. Service calls `repo.find_by_id(note_id)`
6. If note is `None` → `NoteNotFoundError` → route catches → 404
7. If `note.user_id != user_id` → `NoteNotFoundError` → 404 (info-hiding)
8. If `note.is_deleted` → `NoteNotFoundError` → 404
9. Otherwise, service returns the `Note` aggregate
10. Route converts `Note` → `NoteDTO` (drops `user_id`, `is_deleted`)
11. Response: `200 OK` + JSON-serialized `NoteDTO`

---

## Alternative & Exception Flows

| Scenario | Response | Notes |
|----------|----------|-------|
| Malformed UUID in path | `422 Unprocessable Entity` | FastAPI's built-in UUID parser rejects it |
| Note ID doesn't exist | `404 Not Found` | `NoteNotFoundError` translated to 404 |
| Note belongs to another user | `404 Not Found` | Info-hiding (D2) — same response as missing |
| Note is soft-deleted | `404 Not Found` | Info-hiding (D2, D4) — same response as missing |
| Database error | `500 Internal Server Error` | Unhandled — FastAPI's default; acceptable for MVP |

---

## Postconditions

- No state changes. GET is idempotent and side-effect-free.
- Response contains all public note fields; no internal fields leaked.

---

## Implementation Overview

| Layer | File | Change |
|-------|------|--------|
| **Contract** | `backend/app/notes/schemas/note_schemas.py` | Add `NoteDTO` |
| **API** | `backend/app/notes/api/v1/router.py` | Add `GET /notes/{note_id}` handler |
| **Service** | `backend/app/notes/services/note_service.py` | Add `get_note()` + `NoteNotFoundError` |
| **Domain** | `backend/app/notes/models/note.py` | *No change* — read-only aggregate |
| **Repository** | `backend/app/notes/repositories/*` | *No change* — `find_by_id` already exists |

**Nothing changes in the persistence layer.** UC-001 laid the foundation; UC-002 harvests it.

---

## Traceability — Sequence Step → Code

| Step | Purpose | Code Location |
|------|---------|---------------|
| 2 | UUID validation | FastAPI path parameter parsing |
| 3 | Dependency injection | `get_session`, `get_current_user_id`, `get_note_service` |
| 4 | Route → service | `router.py::get_note()` |
| 5 | Load from DB | `SQLAlchemyNoteRepository::find_by_id()` |
| 6–8 | Info-hiding checks | `NoteService::get_note()` |
| 10 | DTO conversion | `router.py::get_note()` (mapping to `NoteDTO`) |

---

## Known Gaps

1. **Auth is placeholder** — deferred to horizontal slice
2. **`is_deleted` check is theoretical for now** — no path currently sets it (UC-004 will)
3. **No list endpoint** — GETting a single note by ID doesn't include listing all notes; that's a separate UC

---

## Related Use Cases

- **UC-001 Create Note** — produces the notes this UC reads
- **UC-003 Edit Note** — reuses `NoteDTO` for its response; requires View to be functional first
- **UC-004 Delete Note** — will set `is_deleted = true`, making notes disappear from View
- **UC-005 Restore Note** — reverses UC-004; makes notes visible again in View