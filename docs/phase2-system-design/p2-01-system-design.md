# Phase 2: System Design
## Apple Notes Clone

**Version:** 1.0 | **Status:** Complete | **Date:** July 2026

---

## 1. Layered Architecture

```
┌─────────────────────────────────────────────────┐
│  PRESENTATION LAYER (Frontend)                  │
│  Next.js + React + TypeScript + Tailwind        │
├─────────────────────────────────────────────────┤
│  APPLICATION LAYER (Backend Services)           │
│  FastAPI + Pydantic (async, type-safe)          │
├─────────────────────────────────────────────────┤
│  DOMAIN LAYER (Business Logic)                  │
│  Services: NoteService, FolderService, etc.     │
├─────────────────────────────────────────────────┤
│  INFRASTRUCTURE LAYER (Persistence)             │
│  SQLAlchemy ORM + PostgreSQL                    │
└─────────────────────────────────────────────────┘
```

**Data Flow:** Request → Presentation → Application → Domain → Infrastructure → Database

---

## 2. Component Decomposition

| Layer | Component | Responsibility |
|-------|-----------|-----------------|
| **Presentation** | Frontend (Next.js) | UI rendering, user interactions, state management (React hooks/Context) |
| **Application** | API Routes (FastAPI) | HTTP request handling, validation (Pydantic), routing |
| **Domain** | NoteService | Create, read, update, delete notes; auto-save logic |
| **Domain** | FolderService | Create, organize, move folders; hierarchy management |
| **Domain** | SearchService | Full-text search implementation |
| **Domain** | AuthService | User signup, login, password hashing (bcrypt), JWT generation |
| **Infrastructure** | Repository Layer | Database queries (SQLAlchemy), CRUD operations |
| **Infrastructure** | Database | PostgreSQL (users, folders, notes tables) |

---

## 3. API Design Strategy

**Style:** REST (JSON request/response)

**Base URL:** `/api`

**Authentication:** JWT token in `Authorization: Bearer {token}` header

**Response Format:**
```json
{
  "status": "success|error",
  "data": {},
  "errors": []
}
```

---

## 4. REST API Endpoints

### Authentication
| Method | Path | Body | Response | FR |
|--------|------|------|----------|-----|
| POST | `/auth/signup` | `{email, password}` | `{user_id, email, token}` | FR-001 |
| POST | `/auth/login` | `{email, password}` | `{user_id, email, token}` | FR-001 |
| POST | `/auth/logout` | - | `{status: "success"}` | FR-001 |

### Notes
| Method | Path | Body | Response | FR |
|--------|------|------|----------|-----|
| POST | `/notes` | `{title, content, folder_id}` | `{note_id, title, content, created_at}` | FR-002 |
| GET | `/notes/{id}` | - | `{note_id, title, content, created_at, updated_at, is_pinned}` | FR-003 |
| PUT | `/notes/{id}` | `{title?, content?}` | `{note_id, title, content, updated_at}` | FR-004 |
| DELETE | `/notes/{id}` | - | `{status: "success"}` | FR-005 |
| GET | `/notes` | `?folder_id=X&sort=date` | `[{note_id, title, preview, updated_at, is_pinned}]` | FR-009 |

### Folders
| Method | Path | Body | Response | FR |
|--------|------|------|----------|-----|
| POST | `/folders` | `{name, parent_folder_id?}` | `{folder_id, name, parent_folder_id}` | FR-006 |
| PUT | `/folders/{id}` | `{name}` | `{folder_id, name}` | FR-006 |
| DELETE | `/folders/{id}` | - | `{status: "success"}` | FR-006 |
| GET | `/folders` | - | `[{folder_id, name, parent_folder_id}]` | FR-006 |

### Search
| Method | Path | Query | Response | FR |
|--------|------|-------|----------|-----|
| GET | `/search` | `?q=query&folder_id=X` | `[{note_id, title, preview, match_context}]` | FR-007 |

### Note Pin/Unpin
| Method | Path | Body | Response | FR |
|--------|------|------|----------|-----|
| POST | `/notes/{id}/pin` | - | `{note_id, is_pinned: true}` | FR-008 |
| POST | `/notes/{id}/unpin` | - | `{note_id, is_pinned: false}` | FR-008 |

---

## 5. Database Schema

### users table
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);
```

### folders table
```sql
CREATE TABLE folders (
    folder_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    parent_folder_id UUID REFERENCES folders(folder_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_folders_user_id ON folders(user_id);
CREATE INDEX idx_folders_parent_id ON folders(parent_folder_id);
CREATE UNIQUE INDEX idx_folders_name_depth ON folders(user_id, parent_folder_id, name);
```

### notes table
```sql
CREATE TABLE notes (
    note_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    folder_id UUID NOT NULL REFERENCES folders(folder_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_folder_id ON notes(folder_id);
CREATE INDEX idx_notes_created_at ON notes(created_at DESC);
CREATE INDEX idx_notes_updated_at ON notes(updated_at DESC);
CREATE INDEX idx_notes_is_deleted ON notes(is_deleted);
CREATE INDEX idx_notes_is_pinned ON notes(is_pinned);
```

**Full-Text Search:** PostgreSQL `tsvector` on `title` and `content` columns (Phase 2+)

---

## 6. Data Flow: Create Note Example

```
1. User enters title + content → Frontend
2. Frontend POST /notes {title, content, folder_id}
3. FastAPI validates (Pydantic) → AuthService verifies JWT
4. NoteService.create_note(user_id, folder_id, title, content)
5. NoteRepository.insert(note) → SQLAlchemy
6. SQL: INSERT INTO notes (...) → PostgreSQL
7. Return {note_id, title, content, created_at}
8. Frontend receives, updates note list
```

---

## 7. Data Flow: Search Notes Example

```
1. User types query in search bar → Frontend (debounced 150ms)
2. Frontend GET /search?q={query}&folder_id={X}
3. FastAPI validates query, checks auth
4. SearchService.search(user_id, folder_id, query)
5. SQL: SELECT * FROM notes WHERE ... AND tsvector @@ tsquery
6. Return [{note_id, title, preview, match_context}]
7. Frontend displays results with highlighting
```

---

## 8. Key Design Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **REST over gRPC** | Simple, browser-native, JSON compatible | Slightly higher latency than gRPC |
| **JWT (stateless)** | Horizontal scalability, no session storage | Less granular revocation (handled by expiry) |
| **PostgreSQL over NoSQL** | ACID guarantees, relational data (folders), SQL performance | Requires schema migrations |
| **SQLAlchemy ORM** | Type-safe, prevents SQL injection, async support | Slight performance overhead vs. raw SQL |
| **Soft delete (is_deleted)** | User recovery safety, data audit trail | Query complexity (WHERE is_deleted = FALSE) |
| **Indexes on created_at, updated_at** | Fast sorting in note list | Extra write overhead during INSERT/UPDATE |
| **Full-text search in DB** | Fast, scalable, leverages PostgreSQL | Limited fuzzy matching (Phase 2+) |

---

## 9. Next Phase

**Phase 3: Architecture Design**
- Hexagonal/Ports & Adapters pattern
- Service interfaces (what each service exposes)
- Dependency injection & wiring
- Error handling strategy

---

**Status:** Ready for Phase 3 Architecture Design

