import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import session_manager


@pytest.fixture
def client():
    session_manager.clear_all_sessions()
    with TestClient(app) as test_client:
        yield test_client
    session_manager.clear_all_sessions()


def test_15_create_session_api_demo_response_envelope(client):
    """15. Session API returns correct response envelope for demo mode."""
    response = client.post("/api/v1/sessions", json={"mode": "demo"})
    assert response.status_code == 201

    payload = response.json()
    assert payload["success"] is True
    assert payload["error"] is None

    data = payload["data"]
    assert "sessionId" in data
    assert data["sessionId"].startswith("sess_")
    assert data["mode"] == "demo"
    assert data["status"] == "created"


def test_create_session_api_research_mode(client):
    """Verify POST /api/v1/sessions handles research mode correctly."""
    response = client.post("/api/v1/sessions", json={"mode": "research"})
    assert response.status_code == 201

    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["mode"] == "research"


def test_create_session_api_invalid_mode_rejected(client):
    """Verify POST /api/v1/sessions rejects invalid modes with HTTP 400 and standard API envelope."""
    response = client.post("/api/v1/sessions", json={"mode": "invalid_mode"})
    assert response.status_code == 400

    payload = response.json()
    assert payload["success"] is False
    assert payload["data"] is None
    assert payload["error"]["code"] == "INVALID_MODE"
    assert "Invalid session mode" in payload["error"]["message"]


def test_get_session_api_summary(client):
    """Verify GET /api/v1/sessions/{sessionId} returns correct summary Data model."""
    create_res = client.post("/api/v1/sessions", json={"mode": "demo"})
    session_id = create_res.json()["data"]["sessionId"]

    get_res = client.get(f"/api/v1/sessions/{session_id}")
    assert get_res.status_code == 200

    payload = get_res.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["sessionId"] == session_id
    assert data["mode"] == "demo"
    assert data["status"] == "created"
    assert data["cluesCount"] == 0
    assert data["consecutiveIdkCount"] == 0
    assert data["totalIdkCount"] == 0


def test_get_session_api_not_found(client):
    """Verify GET /api/v1/sessions/{sessionId} returns 404 with standard API envelope."""
    get_res = client.get("/api/v1/sessions/non_existent_id")
    assert get_res.status_code == 404

    payload = get_res.json()
    assert payload["success"] is False
    assert payload["data"] is None
    assert payload["error"]["code"] == "SESSION_NOT_FOUND"
    assert "not found" in payload["error"]["message"]


def test_analytics_export_unauthorized_without_token(client):
    """Verify GET /api/v1/analytics/export returns 401 Unauthorized without admin token."""
    res = client.get("/api/v1/analytics/export")
    assert res.status_code == 401
    payload = res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "UNAUTHORIZED"


def test_analytics_export_authorized_with_admin_token(client):
    """Verify GET /api/v1/analytics/export returns 200 OK with valid admin token."""
    from app.config import settings
    res = client.get("/api/v1/analytics/export", headers={"x-admin-token": settings.ANALYTICS_ADMIN_TOKEN})
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert "sessions" in payload["data"]

