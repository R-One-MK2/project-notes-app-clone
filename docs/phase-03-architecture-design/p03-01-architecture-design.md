# Phase 3: Architecture Design
## Hexagonal Architecture (Ports & Adapters)

**Version:** 1.0 | **Status:** Complete | **Date:** July 2026

---

## 1. Hexagonal Architecture Overview

**Core Principle:** Core business logic (domain) is isolated from external dependencies (adapters).

```
         Driving Adapters (Input)
                    |
         HTTP API (FastAPI) ← User
                    |
        ╔═══════════════════╗
        ║   CORE DOMAIN     ║
        ║   (Business Logic)║
        ╚═══════════════════╝
                    |
         Driven Adapters (Output)
                    |
         Database (PostgreSQL)
         Email Service (future)
```

---

## 2. Ports & Adapters Structure

### Core Domain (Ports define contracts)

**Port: NotePort**
- `create_note(user_id, folder_id, title, content) → Note`
- `get_note(user_id, note_id) → Note`
- `update_note(user_id, note_id, title, content) → Note`
- `delete_note(user_id, note_id) → void`
- `search_notes(user_id, query, folder_id) → List[Note]`

**Port: FolderPort**
- `create_folder(user_id, name, parent_id?) → Folder`
- `get_folders(user_id) → List[Folder]`
- `move_note(user_id, note_id, folder_id) → Note`
- `delete_folder(user_id, folder_id) → void`

**Port: AuthPort**
- `signup(email, password) → User`
- `login(email, password) → Token`
- `verify_token(token) → user_id`

**Port: PersistencePort (Repository interface)**
- `find_note(note_id) → Note`
- `save_note(note) → void`
- `delete_note(note_id) → void`
- `find_all_notes(user_id, folder_id) → List[Note]`

---

### Adapters (Implement ports)

**Driving Adapter: HTTP API (FastAPI)**
- Converts HTTP requests → port calls
- Example: `POST /notes` → `NotePort.create_note()`
- Handles routing, validation, error responses

**Driven Adapter: Database (SQLAlchemy/PostgreSQL)**
- Implements `PersistencePort`
- Converts domain objects ↔ SQL
- Handles transactions, indexes, constraints

**Driven Adapter: Authentication (bcrypt + JWT)**
- Implements `AuthPort`
- Password hashing/verification
- JWT token generation/verification

---

## 3. Dependency Injection (Wiring)

**Principle:** Core domain does NOT know about adapters. Adapters implement port interfaces.

```python
# Core domain (no database imports)
class NoteService:
    def __init__(self, persistence_port: PersistencePort):
        self.db = persistence_port
    
    def create_note(self, user_id, folder_id, title, content):
        # Pure business logic
        note = Note(user_id, folder_id, title, content)
        self.db.save_note(note)  # Calls abstract port
        return note

# Adapter layer (wires concrete implementations)
from adapters.database import SQLAlchemy_NoteRepository

# Dependency injection
repo = SQLAlchemy_NoteRepository()  # Concrete implementation
note_service = NoteService(repo)    # Injected into core
```

---

## 4. Service Interfaces (Ports)

| Service | Port Interface | Responsibility |
|---------|--------|-----------------|
| **NoteService** | NotePort | CRUD notes, auto-save logic |
| **FolderService** | FolderPort | Folder hierarchy, organization |
| **SearchService** | SearchPort | Full-text search, indexing |
| **AuthService** | AuthPort | Signup, login, JWT, bcrypt |
| **UserService** | UserPort | User profile, data isolation |

**All services:**
- Take port (interface) in constructor
- Operate on domain objects (User, Note, Folder)
- Have NO knowledge of HTTP, database, or libraries

---

## 5. Domain Objects (Core)

### Note (Aggregate Root)
```python
class Note:
    note_id: UUID
    user_id: UUID
    folder_id: UUID
    title: str
    content: str
    is_pinned: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    def update_content(self, new_content: str):
        self.content = new_content
        self.updated_at = now()
```

### Folder (Aggregate Root)
```python
class Folder:
    folder_id: UUID
    user_id: UUID
    parent_folder_id: Optional[UUID]
    name: str
    created_at: datetime
    updated_at: datetime
    
    def is_valid_nesting(self) -> bool:
        # Validate depth <= 5
        return True
```

### User (Aggregate Root)
```python
class User:
    user_id: UUID
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
    
    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)
```

---

## 6. Error Handling Strategy

**Custom Exceptions (Domain Layer):**
```python
class DomainException(Exception): pass
class NoteNotFound(DomainException): pass
class FolderNotEmpty(DomainException): pass
class UnauthorizedAccess(DomainException): pass
class InvalidFolderDepth(DomainException): pass
```

**HTTP Response Mapping (Adapter Layer):**
```
NoteNotFound → 404 Not Found
UnauthorizedAccess → 401 Unauthorized
InvalidFolderDepth → 400 Bad Request
```

---

## 7. Transactions & Data Consistency

**ACID Guarantees (Database Level):**
- **Create Note:** Atomic insert + timestamp
- **Update Note:** Single UPDATE statement (idempotent)
- **Delete Note:** UPDATE is_deleted = true (soft delete)
- **Move Note:** UPDATE folder_id (atomic)

**Auto-Save Logic (Application Level):**
- Debounce 3 seconds (frontend)
- Send single PUT request
- Database handles one write

---

## 8. Key Architectural Decisions

| Decision | Why | Trade-off |
|----------|-----|-----------|
| **Hexagonal Pattern** | Core logic isolated from frameworks | Extra abstraction layer |
| **Port Interfaces** | Testable (mock adapters) | More code upfront |
| **Dependency Injection** | Loose coupling, swap adapters | Requires container setup |
| **ACID Transactions** | Data consistency guaranteed | Performance slight overhead |
| **Domain Exceptions** | Semantic error handling | Requires mapping to HTTP |

---

## 9. Next Phase

**Phase 4: Modular Design**
- Service class signatures (methods, parameters)
- Repository interfaces (query methods)
- DTOs (Data Transfer Objects)
- Validation logic placement

---

**Status:** Ready for Phase 4 Modular Design

