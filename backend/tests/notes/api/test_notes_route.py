"""
Tests for the Notes API route (UC-01: Create Note).

TEST PLAN OVERVIEW
Traceability: Every test cites an Acceptance Criterion (AC-NN) from
docs/phase-05-implementation/p05-uc01-create-note.md.

Rule: No test without an AC. If a behavior needs testing but has no AC,
add the AC to the UC doc first, then write the test.

SESSION 1 — HTTP Plumbing (COMPLETE)
Goal: Establish the HTTP boundary. Route exists, responds, is observable.

  [x] Cycle 1: Route returns HTTP 200                              (regression)
  [x] Cycle 2: Response body is {"status": "success"}              (regression)
  [x] Cycle 3: Request is logged at INFO level                     → AC-33
  [x] Cycle 4: Log message includes HTTP method and path           → AC-34
  [x] Cycle 5: Refactor — extract router to app/notes/api/v1/

SESSION 2 — HTTP Boundary Validation (IN PROGRESS)
Goal: Enforce structural validation via Pydantic. Reject malformed requests
      with 422 before the domain is invoked.

  [x] Cycle 6:  Missing title returns 422                          → AC-02
  [x] Cycle 7:  Non-string title returns 422                       → AC-03
  [x] Cycle 8:  Missing folder_id returns 422                      → AC-04
  [x] Cycle 9:  Invalid UUID for folder_id returns 422             → AC-05
  [x] Cycle 10: Missing content is accepted (content optional)     → AC-06
  [x] Cycle 11: Valid request still returns 200 (regression)       → AC-01
  [x] Cycle 12: Refactor — extract CreateNoteRequest to schemas.py


SESSION 3 — Domain Layer (Value Objects + Aggregate)
Goal: Build the domain layer in pure Python. No FastAPI, no Pydantic, no DB.
      Business rules enforced by Value Objects and aggregate invariants.

Cycles:
  [ ] Cycle 13: Title rejects empty string                       → AC-07
  [ ] Cycle 14: Title rejects whitespace-only string             → AC-08
  [ ] Cycle 15: Title strips leading/trailing whitespace         → AC-10
  [ ] Cycle 16: Title rejects string over 255 chars              → AC-09
  [ ] Cycle 17: Title equality (VOs are equal if values are)     → (extra)
  [ ] Cycle 18: Content rejects string over 1MB                  → AC-11
  [ ] Cycle 19: Content accepts empty string                     → AC-12
  [ ] Cycle 20: Note.create() generates unique note_id           → AC-13
  [ ] Cycle 21: Note.create() sets created_at to now             → AC-14
  [ ] Cycle 22: Note.create() sets updated_at == created_at      → AC-15
  [ ] Cycle 23: Note.create() defaults to unpinned, not-deleted  → AC-16


FUTURE SESSIONS (out of scope for now)

Session 3 — Domain Layer (Value Objects, Note aggregate)   → AC-07..AC-16
Session 4 — Domain Service (NoteService, folder ownership) → AC-17..AC-20
Session 5 — Persistence Adapters (SQLAlchemy)              → AC-21..AC-24
Session 6 — Authentication & Authorization (JWT)           → AC-25..AC-29
Session 7 — Response DTOs (NoteDTO, 201 status)            → AC-30..AC-32
Session 8 — E2E Integration Tests                          → AC-36..AC-37
"""

import logging
from uuid import UUID, uuid4

# Import ORM models to register with Base.metadata
from app.notes.repositories.orm import NoteORM  # noqa: F401
from app.organization.repositories.orm import FolderORM  # noqa: F401

# ------------------------------------------------
# Test fixtures / helpers
# ------------------------------------------------

# A minimally valid payload used across happy-path and regression tests.
# Session 2 introduces validation, so all tests must send a valid body now.
TEST_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
TEST_FOLDER_ID = UUID("550e8400-e29b-41d4-a716-446655440000")
TEST_NOTE_ID = UUID("00000000-0000-0000-0000-000000000001")

VALID_PAYLOAD = {
    "title": "Grocery List",
    "content": "Milk, Eggs, Bread",
    "folder_id": str(TEST_FOLDER_ID),
}

UPDATED_BODY = {"title": "Updated Title", "content": "Updated Content"}

# ------------------------------------------------
# SESSION 1 — HTTP Plumbing
# ------------------------------------------------


def test_valid_request_returns_success(client):
    """
    AC-01: Valid, complete request returns 200 with {"status": "success"}.

    Regression test for the happy path. Guards against overzealous
    validation that could reject legitimate requests.
    Requirement: FR-002 — Create Note.
    """
    response = client.post("/api/v1/notes", json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert "note_id" in body


def test_post_notes_logs_at_info_level(client, caplog):
    """
    AC-33: Every POST is logged at INFO level.

    Enforced at the route/middleware layer.
    Requirement: NFR-005 (observability).
    """
    caplog.set_level(logging.INFO)

    client.post("/api/v1/notes", json=VALID_PAYLOAD)

    info_records = [r for r in caplog.records if r.levelname == "INFO"]
    assert len(info_records) >= 1, "Expected at least one INFO log record"


def test_post_notes_log_includes_method_and_path(client, caplog):
    """
    AC-34: Log message includes HTTP method and path.

    Actionable logs must identify which request they describe.
    Requirement: NFR-005 (observability).
    """
    caplog.set_level(logging.INFO)

    client.post("/api/v1/notes", json=VALID_PAYLOAD)

    assert "POST" in caplog.text
    assert "/api/v1/notes" in caplog.text


# ------------------------------------------------
# SESSION 2 — HTTP Boundary Validation
# (Tests will be added here one at a time, following RED → GREEN → REFACTOR)
# ------------------------------------------------
def test_missing_title_returns_422(client):
    """
    AC-02: Missing title field returns 422.

    Enforced at the HTTP boundary via Pydantic.
    Requirement: FR-002 — title is required.
    """
    # Payload WITHOUT title
    payload = {
        "content": "some content",
        "folder_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    response = client.post("/api/v1/notes", json=payload)
    assert response.status_code == 422


def test_title_wrong_type_returns_422(client):
    """
    AC-03: Non-string title returns 422.

    Enforced at the HTTP boundary via Pydantic.
    Requirement: FR-002 — title must be a string.
    """
    payload = {
        "title": 12345,  # ← integer, not a string
        "content": "some content",
        "folder_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    response = client.post("/api/v1/notes", json=payload)
    assert response.status_code == 422


def test_missing_folder_id_returns_422(client):
    """
    AC-04: Missing folder_id returns 422.

    Enforced at the HTTP boundary via Pydantic.
    Requirement: FR-002 — folder_id required; FR-006 — every note belongs to a folder.
    """

    payload = {
        "title": "sample title",
        "content": "some content",
    }

    response = client.post("/api/v1/notes", json=payload)
    assert response.status_code == 422


def test_invalid_folder_id_returns_422(client):
    """
    AC-05: Malformed UUID folder_id returns 422.

    Enforced at the HTTP boundary via Pydantic's UUID type.
    Requirement: FR-002 — folder_id must be valid UUID.
    Requirement: NFR-002 — reject malformed input at boundary.
    """

    payload = {"title": "sample title", "folder_id": "not-a-uuid"}

    response = client.post("/api/v1/notes", json=payload)
    assert response.status_code == 422


def test_missing_content_is_optional_201(client):
    """
    AC-06: Missing content is accepted (content is optional).

    Content is not required; it defaults to empty string.
    Requirement: FR-002 — content is optional on note creation.
    """
    payload = {
        "title": "sample title",
        "folder_id": "550e8400-e29b-41d4-a716-446655440000",
        # No content key
    }

    response = client.post("/api/v1/notes", json=payload)
    assert response.status_code == 201


# ------------------------------------------------
# UC-002 — GET /api/v1/notes/{note_id}
# ------------------------------------------------


def test_get_existing_note_returns_dto(client):
    """
    UC-002 AC-01: GET existing note returns 200 with NoteDTO.
    Requirement: FR-003 — retrieve a note.
    """
    create_response = client.post("/api/v1/notes", json=VALID_PAYLOAD)
    note_id = create_response.json()["note_id"]

    response = client.get(f"/api/v1/notes/{note_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["note_id"] == note_id
    assert body["title"] == VALID_PAYLOAD["title"]
    assert body["content"] == VALID_PAYLOAD["content"]


def test_get_missing_note_returns_404(client):
    """
    UC-002 AC-03: GET nonexistent note returns 404.
    Requirement: FR-003 — cannot view a note that doesn't exist.
    """
    response = client.get(f"/api/v1/notes/{uuid4()}")
    assert response.status_code == 404


def test_get_malformed_uuid_returns_422(client):
    """
    UC-002 AC-02: GET with malformed UUID in path returns 422.
    Enforced by FastAPI path parameter parsing.
    Requirement: FR-003 — note_id must be valid UUID.
    """
    response = client.get("/api/v1/notes/not-a-uuid")
    assert response.status_code == 422


def test_get_note_response_shape(client):
    """AC-04: Response body contains all seven public NoteDTO fields."""

    create_response = client.post("/api/v1/notes", json=VALID_PAYLOAD)
    note_id = create_response.json()["note_id"]

    response = client.get(f"/api/v1/notes/{note_id}")
    body = response.json()

    assert "note_id" in body
    assert "title" in body
    assert "content" in body
    assert "folder_id" in body
    assert "is_pinned" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_get_note_hides_internal_fields(client):
    """AC-05: Response never exposes user_id or is_deleted."""
    create_response = client.post("/api/v1/notes", json=VALID_PAYLOAD)
    note_id = create_response.json()["note_id"]

    response = client.get(f"/api/v1/notes/{note_id}")
    body = response.json()

    assert "user_id" not in body
    assert "is_deleted" not in body


# ============================================================
# UC-003 — PUT /api/v1/notes/{note_id}
# ============================================================


def test_update_existing_note_returns_updated_dto(client):
    """
    UC-003 AC-01: PUT existing note returns 200 with updated NoteDTO.
    """
    create_response = client.post("/api/v1/notes", json=VALID_PAYLOAD)
    note_id = create_response.json()["note_id"]

    response = client.put(f"/api/v1/notes/{note_id}", json=UPDATED_BODY)

    assert response.status_code == 200
    body = response.json()
    assert body["note_id"] == note_id
    assert body["title"] == "Updated Title"
    assert body["content"] == "Updated Content"


def test_update_missing_note_returns_404(client):
    """
    UC-003 AC-02: PUT nonexistent note returns 404.
    """
    response = client.put(f"/api/v1/notes/{TEST_NOTE_ID}", json=UPDATED_BODY)
    assert response.status_code == 404


def test_update_malformed_uuid_returns_422(client):
    """
    UC-003 AC-03: PUT with malformed UUID returns 422.
    """
    response = client.put("/api/v1/notes/random-not-uuid", json=UPDATED_BODY)
    assert response.status_code == 422


def test_update_missing_title_returns_422(client):
    """
    UC-003 AC-04: PUT missing title in body returns 422.
    """
    create_response = client.post("/api/v1/notes", json=VALID_PAYLOAD)
    note_id = create_response.json()["note_id"]

    response = client.put(
        f"/api/v1/notes/{note_id}", json={"content": "No title, just content"}
    )
    assert response.status_code == 422


def test_update_content_is_optional(client):
    """
    UC-003 AC-05: PUT accepts payload with only title; content defaults to empty.
    """
    create_response = client.post("/api/v1/notes", json=VALID_PAYLOAD)
    note_id = create_response.json()["note_id"]

    response = client.put(
        f"/api/v1/notes/{note_id}", json={"title": "Only title, no content"}
    )
    assert response.status_code == 200
    assert response.json()["content"] == ""


def test_update_ignores_unknown_body_fields(client):
    """
    UC-003 AC-06: PUT silently ignores fields like folder_id and user_id.
    Attacker cannot hijack ownership or move notes via update body.
    """
    create_response = client.post("/api/v1/notes", json=VALID_PAYLOAD)
    note_id = create_response.json()["note_id"]

    # Get original folder for comparison
    get_response = client.get(f"/api/v1/notes/{note_id}")
    original_folder_id = get_response.json()["folder_id"]

    # Try to hijack
    malicious_body = {
        "title": "Legitimate title",
        "content": "Legitimate content",
        "folder_id": str(uuid4()),  # attempt to move
        "user_id": str(uuid4()),  # attempt to hijack
        "is_deleted": True,  # attempt to delete
    }
    response = client.put(f"/api/v1/notes/{note_id}", json=malicious_body)

    assert response.status_code == 200
    body = response.json()

    # Verify ownership/folder unchanged
    assert body["folder_id"] == original_folder_id


def test_update_end_to_end_create_update_read(client):
    """
    UC-003 AC-12: E2E — Create → PUT → GET returns updated values with bumped updated_at.
    """
    create_response = client.post("/api/v1/notes", json=VALID_PAYLOAD)
    note_id = create_response.json()["note_id"]

    # Initial Get
    initial_get = client.get(f"/api/v1/notes/{note_id}")
    initial_updated_at = initial_get.json()["updated_at"]

    # Update
    client.put(f"/api/v1/notes/{note_id}", json=UPDATED_BODY)

    final_get = client.get(f"/api/v1/notes/{note_id}")
    final_body = final_get.json()

    final_updated_at = final_body["updated_at"]

    assert final_body["title"] == UPDATED_BODY["title"]
    assert final_body["content"] == UPDATED_BODY["content"]
    assert final_updated_at > initial_updated_at


# ============================================================
# UC-004 — GET /api/v1/notes (list notes)
# ============================================================


def test_list_notes_returns_empty_list_when_no_notes(client):
    """GET with no notes created returns 200 with an empty list."""
    response = client.get("/api/v1/notes")

    assert response.status_code == 200
    assert response.json() == []


def test_list_notes_returns_created_notes(client):
    """GET returns every note previously created by this user."""
    client.post("/api/v1/notes", json=VALID_PAYLOAD)
    client.post("/api/v1/notes", json={**VALID_PAYLOAD, "title": "Second note"})

    response = client.get("/api/v1/notes")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    titles = {note["title"] for note in body}
    assert titles == {VALID_PAYLOAD["title"], "Second note"}


def test_list_notes_response_shape(client):
    """Each item in the list contains all seven public NoteDTO fields."""
    client.post("/api/v1/notes", json=VALID_PAYLOAD)

    response = client.get("/api/v1/notes")
    note = response.json()[0]

    assert "note_id" in note
    assert "title" in note
    assert "content" in note
    assert "folder_id" in note
    assert "is_pinned" in note
    assert "created_at" in note
    assert "updated_at" in note


def test_list_notes_hides_internal_fields(client):
    """List items never expose user_id or is_deleted."""
    client.post("/api/v1/notes", json=VALID_PAYLOAD)

    response = client.get("/api/v1/notes")
    note = response.json()[0]

    assert "user_id" not in note
    assert "is_deleted" not in note
