# Phase 1: Requirements Design
## Apple Notes Clone - MVP

**Version:** 1.0 | **Status:** Complete | **Date:** July 2026

---

## 1. Project Overview

Build a single-user notes application replicating Apple Notes core functionality.

**Stack:** FastAPI + SQLAlchemy + PostgreSQL | Next.js + React + TypeScript

**Reference:** Apple Notes (iOS/macOS)

**Out of scope:** Rich text, collaboration, real-time sync, RAG, chat

---

## 2. Functional Requirements

| ID | Requirement | Description |
|----|----|---|
| FR-001 | User Authentication | Signup, login, logout. JWT sessions. Data isolation per user. |
| FR-002 | Create Note | Title + content. Auto-assigned timestamp. Immediate persistence. |
| FR-003 | View Note | Open note in editor. Display metadata (created_at, updated_at). |
| FR-004 | Update Note | Edit title/content inline. Auto-save on 3-second idle. |
| FR-005 | Delete Note | Soft delete to Trash. Permanent delete from Trash. Restore from Trash. |
| FR-006 | Folder Management | Create nested folders (max depth 5). Move notes between folders. Rename/delete folders. |
| FR-007 | Search Notes | Full-text search (title + content). Case-insensitive. Scope: current folder + subfolders. |
| FR-008 | Pin Notes | Mark as favorite. Pinned notes appear at top of list. Persist pin state. |
| FR-009 | Note List | Display notes in current folder. Show title, preview, updated_at. Sort by name or date. |

---

## 3. Non-Functional Requirements

| ID | Requirement | Target |
|----|-----|--------|
| NFR-001 | Performance | API response < 200ms (p95). Search < 500ms. Database indexed. |
| NFR-002 | Security | JWT (HS256). bcrypt password hashing. CORS configured. SQL injection prevention. |
| NFR-003 | Data Integrity | ACID transactions. Atomic writes. No data loss on crash. Soft deletes. |
| NFR-004 | Scalability | Stateless API (horizontal scaling). Connection pooling. Supports 10k+ users. |
| NFR-005 | Usability | Intuitive UI matching Apple Notes. Keyboard shortcuts (Cmd/Ctrl+N, Cmd/Ctrl+F). Clear errors. |
| NFR-006 | Maintainability | SOLID principles. Hexagonal architecture. Test coverage > 70% (business logic). |

---

## 4. Use Cases

| UC | User Goal | Actor | Precondition | Main Flow | Linked FRs |
|----|----|----|----|----|---|
| UC-001 | Create a note and save it | User | Logged in | Click "New" → Enter title/content → Auto-save → Appears in list | FR-002, FR-004, FR-009 |
| UC-002 | Edit a note with auto-save | User | Note open | Click editor → Type → 3 sec pause → Auto-save → "Saved" indicator | FR-003, FR-004 |
| UC-003 | Search and find a note | User | Logged in, has notes | Type in search → Results filter in real-time → Click to open | FR-007, FR-003 |
| UC-004 | Delete a note safely | User | Note selected | Right-click → Confirm delete → Moved to Trash | FR-005 |
| UC-005 | Restore a deleted note | User | Note in Trash | Open Trash → Select note → Restore → Note returns to original folder | FR-005 |
| UC-006 | Organize notes with folders | User | Logged in | Create folder → Move notes via drag-drop → View in subfolder | FR-006, FR-009 |
| UC-007 | Pin important notes | User | Viewing notes | Right-click note → "Pin" → Moves to top with star icon | FR-008, FR-009 |

---

## 5. Acceptance Criteria (by FR)

### FR-001: Authentication
- ✅ User can signup with email + password
- ✅ Duplicate email rejected
- ✅ Login persists session across browser close
- ✅ Logout clears session
- ✅ Unauthenticated requests rejected
- ✅ User A cannot access User B's notes

### FR-002: Create Note
- ✅ Title required (empty title shows error)
- ✅ Saved to database immediately (no "Save" button)
- ✅ Appears in note list instantly
- ✅ Timestamp assigned by server (not client)
- ✅ Content preserved exactly as entered

### FR-003: View Note
- ✅ Note opens in editor view (full content, no truncation)
- ✅ Metadata displayed (created_at, updated_at)
- ✅ Breadcrumb shows folder path

### FR-004: Update Note
- ✅ Edits appear immediately (optimistic UI)
- ✅ Persisted within 3 seconds of typing stop
- ✅ "Saving" indicator shown during save
- ✅ Navigate away with unsaved changes → warning prompt

### FR-005: Delete Note
- ✅ Confirmation dialog shown
- ✅ Deleted note moved to Trash (soft delete)
- ✅ Note restorable from Trash
- ✅ Permanent delete removes from database

### FR-006: Folder Management
- ✅ Create nested folders up to 5 levels deep
- ✅ Folder names unique at same depth
- ✅ Move note to folder via drag-drop or context menu
- ✅ Rename folder (except "Notes" and "Trash")
- ✅ Delete empty folder only
- ✅ Folder structure persists

### FR-007: Search Notes
- ✅ Query matches title and content (case-insensitive)
- ✅ Results update as user types (debounced 150ms)
- ✅ Shows matching note title + content snippet
- ✅ Empty search shows all notes
- ✅ Search scope: current folder + subfolders (toggle for "all notes")

### FR-008: Pin Notes
- ✅ Pin/unpin via context menu
- ✅ Pinned notes appear at top of list
- ✅ Star icon indicates pinned state
- ✅ Pin state persists

### FR-009: Note List
- ✅ Shows notes in current folder only
- ✅ Display: title, preview (first 100 chars), updated_at
- ✅ Default sort: by updated_at (newest first)
- ✅ Sort options: by name (A-Z), by date (old/new)
- ✅ Handles 500+ notes without performance degradation

---

## 6. Data Model

### User
```
user_id (UUID, PK)
email (string, unique)
password_hash (string)
created_at (timestamp)
updated_at (timestamp)
```

### Folder
```
folder_id (UUID, PK)
user_id (UUID, FK → User)
parent_folder_id (UUID, nullable, FK → Folder)
name (string)
created_at (timestamp)
updated_at (timestamp)
```

### Note
```
note_id (UUID, PK)
user_id (UUID, FK → User)
folder_id (UUID, FK → Folder)
title (string)
content (text)
is_pinned (boolean, default false)
is_deleted (boolean, default false)
created_at (timestamp)
updated_at (timestamp)
```

### Relationships
- User (1) → (N) Folder
- User (1) → (N) Note
- Folder (1) → (N) Folder (self-referential nesting)
- Folder (1) → (N) Note

---

## 7. Key Assumptions

1. **Layered Architecture:** Presentation → Application → Domain → Infrastructure
2. **REST API:** JSON request/response. Token-based auth.
3. **Relational Database:** Indexes on user_id, created_at, folder_id
4. **Design Patterns:** Repository (data access), Service (business logic), DTO (data transfer)
5. **Security:** bcrypt (password), JWT (sessions), CORS (cross-origin)
6. **Durability:** ACID transactions. Immediate DB writes before UI confirmation.

---

## 8. Traceability Matrix

| Requirement | Use Case | Phase 6 Test |
|--------|--------|-------|
| FR-001 | UC-001 through UC-007 (all require auth) | TC-001 to TC-020 |
| FR-002 | UC-001 | TC-021 to TC-030 |
| FR-003 | UC-002, UC-003 | TC-031 to TC-040 |
| FR-004 | UC-001, UC-002 | TC-041 to TC-050 |
| FR-005 | UC-004, UC-005 | TC-051 to TC-060 |
| FR-006 | UC-006 | TC-061 to TC-080 |
| FR-007 | UC-003 | TC-081 to TC-100 |
| FR-008 | UC-007 | TC-101 to TC-110 |
| FR-009 | UC-001, UC-006, UC-007 | TC-111 to TC-125 |

---

## 9. Next Phase

**Phase 2: System Design**
- API endpoint specification (REST contract)
- Database schema with indexes and constraints
- Sequence diagrams for key use cases (PlantUML)
- Layered architecture diagram (Presentation, Application, Domain, Infrastructure)

---

**Approved by:** Sree (Developer)  
**Status:** Ready for Phase 2
