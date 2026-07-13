# Phase 4: Modular Design
## Service Classes & Interfaces

**Version:** 1.0 | **Status:** Complete | **Date:** July 2026

---

## 1. Service Class Signatures

### AuthService
```python
class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository
    
    def signup(self, email: str, password: str) -> User:
        # Validate email, hash password, create user
        # Raise: DuplicateEmailError
        pass
    
    def login(self, email: str, password: str) -> str:
        # Verify email + password, generate JWT
        # Raise: InvalidCredentialsError
        # Return: JWT token
        pass
    
    def verify_token(self, token: str) -> UUID:
        # Decode JWT, validate signature
        # Raise: InvalidTokenError
        # Return: user_id
        pass
```

### NoteService
```python
class NoteService:
    def __init__(self, note_repo: NoteRepository):
        self.note_repo = note_repo
    
    def create_note(self, user_id: UUID, folder_id: UUID, 
                   title: str, content: str) -> Note:
        # Validate folder belongs to user
        # Create Note aggregate
        # Save & return
        pass
    
    def get_note(self, user_id: UUID, note_id: UUID) -> Note:
        # Verify ownership, return note
        # Raise: NoteNotFound, UnauthorizedAccess
        pass
    
    def update_note(self, user_id: UUID, note_id: UUID, 
                   title: Optional[str], content: Optional[str]) -> Note:
        # Fetch note, update, persist
        # Update timestamp
        # Raise: NoteNotFound, UnauthorizedAccess
        pass
    
    def delete_note(self, user_id: UUID, note_id: UUID) -> None:
        # Soft delete (set is_deleted=true)
        # Move to Trash folder
        pass
    
    def restore_note(self, user_id: UUID, note_id: UUID, 
                    original_folder_id: UUID) -> Note:
        # Restore from trash to original folder
        pass
    
    def pin_note(self, user_id: UUID, note_id: UUID) -> Note:
        # Set is_pinned=true
        pass
    
    def unpin_note(self, user_id: UUID, note_id: UUID) -> Note:
        # Set is_pinned=false
        pass
```

### FolderService
```python
class FolderService:
    def __init__(self, folder_repo: FolderRepository):
        self.folder_repo = folder_repo
    
    def create_folder(self, user_id: UUID, name: str, 
                     parent_id: Optional[UUID] = None) -> Folder:
        # Validate parent depth < 5
        # Validate name unique at depth
        # Create Folder aggregate
        pass
    
    def get_folders(self, user_id: UUID) -> List[Folder]:
        # Return all folders for user (tree structure)
        pass
    
    def rename_folder(self, user_id: UUID, folder_id: UUID, 
                     new_name: str) -> Folder:
        # Verify ownership & not system folders (Notes, Trash)
        # Update & return
        pass
    
    def delete_folder(self, user_id: UUID, folder_id: UUID) -> None:
        # Verify folder is empty (no notes)
        # Raise: FolderNotEmpty, CannotDeleteSystemFolder
        pass
    
    def move_note(self, user_id: UUID, note_id: UUID, 
                 target_folder_id: UUID) -> Note:
        # Verify note & folder ownership
        # Update note.folder_id
        pass
```

### SearchService
```python
class SearchService:
    def __init__(self, note_repo: NoteRepository):
        self.note_repo = note_repo
    
    def search_notes(self, user_id: UUID, query: str, 
                    folder_id: Optional[UUID] = None) -> List[Note]:
        # Full-text search in title + content
        # Filter by user_id, folder_id, is_deleted=false
        # Return results with match context
        pass
```

---

## 2. Repository Interfaces (Ports)

### NoteRepository (Persistence Port)
```python
class NoteRepository(ABC):
    @abstractmethod
    def find_by_id(self, note_id: UUID) -> Optional[Note]:
        pass
    
    @abstractmethod
    def find_all_by_user(self, user_id: UUID) -> List[Note]:
        pass
    
    @abstractmethod
    def find_by_folder(self, folder_id: UUID) -> List[Note]:
        pass
    
    @abstractmethod
    def find_by_user_folder(self, user_id: UUID, folder_id: UUID) -> List[Note]:
        pass
    
    @abstractmethod
    def find_pinned(self, user_id: UUID, folder_id: UUID) -> List[Note]:
        pass
    
    @abstractmethod
    def search(self, user_id: UUID, query: str, 
              folder_id: Optional[UUID]) -> List[Note]:
        pass
    
    @abstractmethod
    def save(self, note: Note) -> None:
        pass
    
    @abstractmethod
    def delete(self, note_id: UUID) -> None:
        pass
    
    @abstractmethod
    def update(self, note: Note) -> None:
        pass
```

### FolderRepository (Persistence Port)
```python
class FolderRepository(ABC):
    @abstractmethod
    def find_by_id(self, folder_id: UUID) -> Optional[Folder]:
        pass
    
    @abstractmethod
    def find_by_user(self, user_id: UUID) -> List[Folder]:
        pass
    
    @abstractmethod
    def find_root_folders(self, user_id: UUID) -> List[Folder]:
        pass
    
    @abstractmethod
    def find_children(self, parent_id: UUID) -> List[Folder]:
        pass
    
    @abstractmethod
    def save(self, folder: Folder) -> None:
        pass
    
    @abstractmethod
    def update(self, folder: Folder) -> None:
        pass
    
    @abstractmethod
    def delete(self, folder_id: UUID) -> None:
        pass
```

### UserRepository (Persistence Port)
```python
class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> None:
        pass
```

---

## 3. DTOs (Data Transfer Objects)

**Purpose:** Serialize domain objects ↔ JSON without exposing password_hash

### NoteDTO
```python
class NoteDTO(BaseModel):
    note_id: UUID
    title: str
    content: str
    is_pinned: bool
    folder_id: UUID
    created_at: datetime
    updated_at: datetime
```

### FolderDTO
```python
class FolderDTO(BaseModel):
    folder_id: UUID
    name: str
    parent_folder_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
```

### UserDTO
```python
class UserDTO(BaseModel):
    user_id: UUID
    email: str
    created_at: datetime
```

### SignupRequest
```python
class SignupRequest(BaseModel):
    email: EmailStr
    password: str  # Validated: min 8 chars, complexity
```

### LoginRequest
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

### CreateNoteRequest
```python
class CreateNoteRequest(BaseModel):
    title: str  # Required, max 255 chars
    content: str  # Optional
    folder_id: UUID
```

### UpdateNoteRequest
```python
class UpdateNoteRequest(BaseModel):
    title: Optional[str]
    content: Optional[str]
```

---

## 4. Validation Rules

| Entity | Field | Rule | Error |
|--------|-------|------|-------|
| User | email | EmailStr (RFC 5322) | InvalidEmailError |
| User | password | min 8 chars | PasswordTooShortError |
| User | password | ≥1 uppercase, ≥1 digit | PasswordComplexityError |
| Note | title | required, max 255 chars | InvalidTitleError |
| Note | content | max 1MB | ContentTooLargeError |
| Folder | name | required, max 255 chars | InvalidFolderNameError |
| Folder | depth | max 5 levels | InvalidFolderDepthError |
| Folder | name | unique at same parent_id | DuplicateFolderNameError |

---

## 5. Exception Hierarchy

```
DomainException (base)
├── AuthenticationError
│   ├── InvalidCredentialsError
│   ├── InvalidTokenError
│   └── UnauthorizedAccessError
├── ValidationError
│   ├── InvalidEmailError
│   ├── PasswordComplexityError
│   ├── InvalidTitleError
│   └── InvalidFolderNameError
├── ResourceError
│   ├── NoteNotFound
│   ├── FolderNotFound
│   └── UserNotFound
└── OperationError
    ├── FolderNotEmpty
    ├── InvalidFolderDepth
    └── DuplicateFolderName
```

---

## 6. Dependency Injection Container

```python
# Container wiring (FastAPI startup)
from fastapi import FastAPI

app = FastAPI()

# Repositories
user_repo = SQLAlchemy_UserRepository(db)
note_repo = SQLAlchemy_NoteRepository(db)
folder_repo = SQLAlchemy_FolderRepository(db)

# Services
auth_service = AuthService(user_repo)
note_service = NoteService(note_repo)
folder_service = FolderService(folder_repo)
search_service = SearchService(note_repo)

# Inject into routes
@app.post("/auth/signup")
def signup(req: SignupRequest, 
          service: AuthService = Depends(lambda: auth_service)):
    return service.signup(req.email, req.password)
```

---

## 7. Key Design Patterns

| Pattern | Usage | Benefit |
|---------|-------|---------|
| **Repository** | Abstract data access | Swap adapters (DB ↔ Mock) |
| **Service** | Encapsulate business logic | Reusable, testable |
| **DTO** | Serialize/deserialize | Decouple domain ↔ API |
| **Dependency Injection** | Wire dependencies | Loose coupling |
| **Factory** | Create domain objects | Centralized validation |
| **Value Object** | Immutable types (email, UUID) | Type safety |

---

## 8. Next Phase

**Phase 5: Coding**
- Implement services (NoteService, FolderService, etc.)
- Implement repositories (SQLAlchemy adapters)
- Implement FastAPI routes
- Implement Next.js components

Hand-code against these signatures without deviation.

---

**Status:** Ready for Phase 5 Coding

