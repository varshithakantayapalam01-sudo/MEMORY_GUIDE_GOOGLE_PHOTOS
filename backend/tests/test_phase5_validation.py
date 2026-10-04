from __future__ import annotations
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.services import session_manager, embedding_service, gemini_client, image_understanding_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_test_sessions():
    yield
    session_manager.clear_all_sessions()


def test_1_synthetic_fallback_blocked_when_allow_synthetic_ai_false():
    """Ensures synthetic fallback fails fast when ALLOW_SYNTHETIC_AI=False."""
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", False), \
         patch.object(gemini_client, "embed_text", side_effect=gemini_client.GeminiAPIError("API error")):

        session = session_manager.create_session(mode="demo")

        res = client.post(
            f"/api/v1/sessions/{session.session_id}/query",
            json={"query": "A vague memory of a birthday party"}
        )
        assert res.status_code == 500
        err = res.json()["error"]
        assert err["code"] == "EMBEDDING_PROVIDER_ERROR"
        assert "synthetic fallback is disabled" in err["message"]


def test_2_production_demo_embeddings_metadata():
    """Ensures demo embeddings contain embedding_source='provider'."""
    embs = embedding_service.load_demo_embeddings(force_reload=True)
    assert len(embs) == 29
    assert "demo_001" in embs
    assert "demo_029" in embs


def test_3_active_pool_max_limit_is_12_and_overflow_enters_reserve():
    """Ensures active pool size limit is strictly 12 and overflow goes to reserve."""
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        session = session_manager.create_session(mode="demo")

        res = client.post(
            f"/api/v1/sessions/{session.session_id}/query",
            json={"query": "That birthday party photo where I think I was wearing pink"}
        )
        assert res.status_code == 200

        updated_session = session_manager.get_session(session.session_id)
        assert len(updated_session.active_candidates) == 12
        assert len(updated_session.reserve_candidates) == 17  # 29 - 12 = 17
        assert len(updated_session.active_candidates) + len(updated_session.reserve_candidates) == 29


def test_4_target_never_permanently_destroyed():
    """Ensures target candidates not in active pool remain safely in reserve pool."""
    with patch.object(settings, "ALLOW_SYNTHETIC_AI", True):
        session = session_manager.create_session(mode="demo")

        res = client.post(
            f"/api/v1/sessions/{session.session_id}/query",
            json={"query": "A vague beach photo"}
        )
        assert res.status_code == 200

        updated_session = session_manager.get_session(session.session_id)
        all_ids = {c.image_id for c in updated_session.active_candidates} | {c.image_id for c in updated_session.reserve_candidates}
        assert len(all_ids) == 29
        assert "demo_001" in all_ids
        assert "demo_029" in all_ids
