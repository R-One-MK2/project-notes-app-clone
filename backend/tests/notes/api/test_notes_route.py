from app.main import app
from fastpi.testclient import TestClient

client = TestClient(app)


def test_post_notes_returns_200():
    response = client.post("/api/v1/notes", json={})
    assert response.status_code == 200
