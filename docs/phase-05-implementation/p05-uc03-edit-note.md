# UC-03: Edit Note

**Goal:** User edits title/content of an open note; changes persist via PUT.
**Realises:** FR-004
**Depends on:** UC-01 (existing notes to edit), UC-02 (note is open in editor)
**Auth:** Deferred to horizontal slice — routes use placeholder `get_current_user_id` for now.

---

## Endpoints

```
PUT  /api/v1/notes/{note_id}    → 200 NoteDTO | 404 | 422
```

---

## Acceptance Criteria

**Legend:** ⚪ Planned · 🟡 In Progress · 🟢 Verified

### HTTP layer

| AC | Description | Status |
|----|------|--------|
| AC-01 | PUT existing note returns 200 + updated `NoteDTO` | ⚪ |
| AC-02 | PUT missing note returns 404 | ⚪ |
| AC-03 | PUT with malformed UUID returns 422 | ⚪ |
| AC-04 | PUT missing `title` returns 422 | ⚪ |
| AC-05 | `folder_id`/`user_id` in body are ignored (moving notes is a separate UC) | ⚪ |

### Domain layer

| AC | Description | Status |
|----|------|--------|
| AC-06 | `Note.rename(title)` replaces title via `Title` VO (revalidates) | ⚪ |
| AC-07 | `Note.edit_content(content)` replaces content via `Content` VO (revalidates) | ⚪ |
| AC-08 | Mutations bump `updated_at` to server time; `created_at` never changes | ⚪ |

### Service layer

| AC | Description | Status |
|----|------|--------|
| AC-09 | `update_note` loads → mutates → persists via `repo.save()` | ⚪ |
| AC-10 | `update_note` verifies ownership BEFORE mutating (no partial mutation on auth failure) | ⚪ |

### Persistence + E2E

| AC | Description | Status |
|----|------|--------|
| AC-11 | `save()` on existing `note_id` performs UPDATE (not duplicate INSERT) — reuses UC-01 idempotency | ⚪ |
| AC-12 | E2E: Create → PUT → GET returns updated values with bumped `updated_at` | ⚪ |

**Total: 12 ACs here + 4 in UC-02 = 16 across ~4 sessions.**

---

## Sessions

UC-02 (view) and UC-03 (edit) ship together on one feature branch — GET and PUT share routes, schemas, and service wiring.

| Session | Scope | ~ACs | Est. |
|---------|-------|------|------|
| **S1** | HTTP plumbing + validation for GET/PUT (routes, schemas) | UC-02 AC-01..03 · AC-01..05 | 2h |
| **S2** | Domain mutators (`rename`, `edit_content`) + Note tests | AC-06..08 | 1.5h |
| **S3** | Service methods (`get_note`, `update_note`) + tests | UC-02 AC-04 · AC-09..10 | 1.5h |
| **S4** | Wire real SQL repo through route + E2E test | AC-11..12 | 1.5h |

**Total: ~6-7 hours across 3-4 sittings.**

---

## Design Decisions

### D1: PUT, not PATCH
Editor always holds the full document. PUT keeps semantics simple, matches autosave retry-safety.

### D2: Domain mutators, not property setters
`Note.rename()` / `Note.edit_content()` preserve encapsulation from UC-01. Each mutator re-validates via the same VOs used at creation, and owns the `updated_at` bump.

### D3: Trash notes are read-only
Soft-deleted notes return 404 for both GET and PUT. Matches Apple Notes UX; enforced at the domain layer so it holds for any future entry point.

### D4: Last-write-wins concurrency
No optimistic locking in MVP. Each PUT is atomic (row-level). Deferred to a future slice if conflicts become a real problem.

### D5: Info-hiding on all lookups
Not-found, unauthorized, and deleted all return 404. Same reasoning as UC-01 (folder authorization).

---

## Known Gaps (defer, don't fix now)

1. **Auth** — placeholder `get_current_user_id` used everywhere; real JWT extraction added as horizontal slice
2. **Autosave debounce** — added when building the frontend; not backend's concern
3. **Concurrency conflict UX** — accepted as last-write-wins for MVP

---

## Related Use Cases

- **UC-01 Create Note** — established the shape UC-03 edits
- **UC-02 View Note** — precondition; shares `get_note`, routes, and DTO
- **UC-05 Delete Note (soft delete)** — sets `is_deleted = true`; UC-03 rejects such notes
- **UC-06 Organize Folders (move note)** — separate UC; PUT here does NOT change `folder_id`
