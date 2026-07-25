# project-notes-app-clone


## Running in Test Mode 

```bash
uv run python -c "
from app.database.engine import SessionFactory
from app.notes.repositories.orm import NoteORM
from app.organization.repositories.orm import FolderORM

with SessionFactory() as session:
    print('=== FOLDERS ===')
    for f in session.query(FolderORM).all():
        print(f'  {f.folder_id} | user={f.user_id}')
    
    print('=== NOTES ===')
    for n in session.query(NoteORM).all():
        print(f'  {n.note_id} | {n.title} | user={n.user_id}')
"
```

```bash
# Stop the server first (Ctrl+C)
rm notes.db

# Restart the server — tables get recreated empty
uv run uvicorn app.main:app --reload

# Reseed the folder (see above)
```