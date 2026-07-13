"""
Tests for the Notes API route (UC-01: Create Note).

===============================================================================
TEST PLAN OVERVIEW
===============================================================================
Traceability: Every test cites an Acceptance Criterion (AC-NN) from
phase5-detailed-use-cases/p5-UC-01-create-note.md.

Rule: No test without an AC. If a behavior needs testing but has no AC,
add the AC to the UC doc first, then write the test.
===============================================================================

SESSION 1 — HTTP Plumbing (COMPLETE)
Goal: Establish the HTTP boundary. Route exists, responds, is observable.

  [x] Cycle 1: Route returns HTTP 200                              (regression)
  [x] Cycle 2: Response body is {"status": "success"}              (regression)
  [x] Cycle 3: Request is logged at INFO level                     → AC-33
  [x] Cycle 4: Log message includes HTTP method and path           → AC-34
  [x] Cycle 5: Refactor — extract router to app/notes/api/v1/

-------------------------------------------------------------------------------
SESSION 2 — HTTP Boundary Validation (IN PROGRESS)
Goal: Enforce structural validation via Pydantic. Reject malformed requests
      with 422 before the domain is invoked.

  [ ] Cycle 6:  Missing title returns 422                          → AC-02
  [ ] Cycle 7:  Non-string title returns 422                       → AC-03
  [ ] Cycle 8:  Missing folder_id returns 422                      → AC-04
  [ ] Cycle 9:  Invalid UUID for folder_id returns 422             → AC-05
  [ ] Cycle 10: Missing content is accepted (content optional)     → AC-06
  [ ] Cycle 11: Valid request still returns 200 (regression)       → AC-01
  [ ] Cycle 12: Refactor — extract CreateNoteRequest to schemas.py

-------------------------------------------------------------------------------
FUTURE SESSIONS (out of scope for now)

Session 3 — Domain Layer (Value Objects, Note aggregate)   → AC-07..AC-16
Session 4 — Domain Service (NoteService, folder ownership) → AC-17..AC-20
Session 5 — Persistence Adapters (SQLAlchemy)              → AC-21..AC-24
Session 6 — Authentication & Authorization (JWT)           → AC-25..AC-29
Session 7 — Response DTOs (NoteDTO, 201 status)            → AC-30..AC-32
Session 8 — E2E Integration Tests                          → AC-36..AC-37
===============================================================================
"""

import logging

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


# -----------------------------------------------------------------------------
# Test fixtures / helpers
# -----------------------------------------------------------------------------

# A minimally valid payload used across happy-path and regression tests.
# Session 2 introduces validation, so all tests must send a valid body now.
VALID_PAYLOAD = {
    "title": "Grocery List",
    "content": "Milk, Eggs, Bread",
    "folder_id": "550e8400-e29b-41d4-a716-446655440000",
}


# -----------------------------------------------------------------------------
# SESSION 1 — HTTP Plumbing
# -----------------------------------------------------------------------------


def test_post_notes_returns_200():
    """
    Route smoke test: POST /api/v1/notes with a valid payload returns 200.

    Regression check — verifies the route wiring itself. Detailed happy-path
    behaviour is covered by AC-01 (Cycle 11).
    """
    response = client.post("/api/v1/notes", json=VALID_PAYLOAD)
    assert response.status_code == 200


def test_post_notes_success_status():
    """
    Route smoke test: response body is {"status": "success"}.

    Regression check — verifies the placeholder response shape.
    Will be replaced by NoteDTO in Session 7 (AC-31).
    """
    response = client.post("/api/v1/notes", json=VALID_PAYLOAD)
    assert response.json() == {"status": "success"}


def test_post_notes_logs_at_info_level(caplog):
    """
    AC-33: Every POST is logged at INFO level.

    Enforced at the route/middleware layer.
    Requirement: NFR-005 (observability).
    """
    caplog.set_level(logging.INFO)

    client.post("/api/v1/notes", json=VALID_PAYLOAD)

    info_records = [r for r in caplog.records if r.levelname == "INFO"]
    assert len(info_records) >= 1, "Expected at least one INFO log record"


def test_post_notes_log_includes_method_and_path(caplog):
    """
    AC-34: Log message includes HTTP method and path.

    Actionable logs must identify which request they describe.
    Requirement: NFR-005 (observability).
    """
    caplog.set_level(logging.INFO)

    client.post("/api/v1/notes", json=VALID_PAYLOAD)

    assert "POST" in caplog.text
    assert "/api/v1/notes" in caplog.text


# -----------------------------------------------------------------------------
# SESSION 2 — HTTP Boundary Validation
# (Tests will be added here one at a time, following RED → GREEN → REFACTOR)
# -----------------------------------------------------------------------------
