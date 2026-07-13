"""
Tests for the Notes API route.

SESSION 1 TEST PLAN: POST /api/v1/notes Plumbing

Goal: Establish the HTTP boundary. No domain, no DB, no validation yet.
Just prove the route exists, responds, and is observable via logs.

Cycles:
  [x] Cycle 1: Route returns HTTP 200
  [x] Cycle 2: Response body is {"status": "success"}
  [x] Cycle 3: Request is logged at INFO level
  [x] Cycle 4: Log message includes HTTP method and path
  [x] Cycle 5: (Refactor) Extract router into app/notes/api/v1/router.py

Out of scope (future sessions):
  - Request body validation (Session 2)
  - Domain layer: Note, Title, Content (Session 3)
  - Authentication / JWT (Session 4)
  - Database persistence (Session 5)

Session 1: HTTP Plumbing (TODAY)
  - Route exists, returns 200
  - Response has structured body
  - Requests are logged

Session 2: Request Validation
  - Pydantic CreateNoteRequest schema
  - Reject empty title (422)
  - Reject missing folder_id (422)
  - Reject content > 1MB (422)

Session 3: Domain Layer
  - Title value object (validation, immutability)
  - Content value object
  - Note aggregate with factory method
  - Domain exceptions

Session 4: Domain Service (with in-memory fake repo)
  - NoteService.create_note()
  - Folder ownership check
  - InMemoryNoteRepository for tests

Session 5: Persistence Adapters
  - SQLAlchemy NoteORM
  - SQLAlchemy_NoteRepository (implements port)
  - Wire real repo via dependency injection

Session 6: Authentication
  - JWT extraction from Authorization header
  - get_current_user_id dependency
  - Reject unauthenticated requests (401)

Session 7: Response DTOs
  - NoteDTO for HTTP response
  - Map domain Note → DTO
  - status_code=201 for creation

Session 8: E2E integration test
  - Full flow with real DB
  - Test isolation, cleanup
"""

import logging

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_post_notes_returns_200():
    """POST /api/v1/notes should return status 200."""
    response = client.post("/api/v1/notes", json={})
    assert response.status_code == 200


def test_post_notes_success_status():
    """Response body should be {'status': 'success'}."""
    response = client.post("/api/v1/notes", json={})
    assert response.json() == {"status": "success"}


def test_post_notes_logs_at_info_level(caplog):
    """
    Cycle 3: At least one INFO-level log record should be emitted
    when POST /api/v1/notes is called.
    """

    caplog.set_level(logging.INFO)
    client.post("/api/v1/notes", json={})

    info_records = [r for r in caplog.records if r.levelname == "INFO"]

    assert len(info_records) >= 1, "Expected atleast one INFO log record"


def test_post_notes_log_includes_method_and_path(caplog):
    """
    Cycle 4: The log message should include HTTP method and path
    so it's actionable in production troubleshooting.
    """

    caplog.set_level(logging.INFO)

    client.post("/api/v1/notes", json={})

    assert "POST" in caplog.text
    assert "/api/v1/notes" in caplog.text
