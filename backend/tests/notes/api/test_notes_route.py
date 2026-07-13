"""
Tests for the Notes API route.

Cycle 1 (RED): POST /api/v1/notes should return HTTP 200.
"""

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
