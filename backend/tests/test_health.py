import os
import sqlite3
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.services import analytics_db


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint_status_200(client):
    """Verify health endpoint returns HTTP 200 status code."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_endpoint_response_content(client):
    """Verify health endpoint response contains expected status, service name, and version."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "memory-guide-api"
    assert data["version"] == "0.1.0"


def test_sqlite_db_initialization(tmp_path):
    """Verify SQLite database initializes correctly at configured path."""
    test_db = str(tmp_path / "test_memory_guide.db")
    analytics_db.init_db(test_db)
    assert os.path.exists(test_db)


def test_sqlite_research_sessions_table_schema(tmp_path):
    """Verify research_sessions table exists with all required core columns."""
    test_db = str(tmp_path / "test_memory_guide.db")
    analytics_db.init_db(test_db)

    with sqlite3.connect(test_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='research_sessions';")
        table = cursor.fetchone()
        assert table is not None
        assert table[0] == "research_sessions"

        cursor.execute("PRAGMA table_info(research_sessions);")
        columns = [col[1] for col in cursor.fetchall()]
        expected_columns = [
            "session_id",
            "started_at",
            "ended_at",
            "library_mode",
            "retrieval_status",
            "original_description",
            "total_time_seconds",
            "questions_to_target",
            "total_idk_count",
            "candidate_reduction_json",
            "clues_json",
            "questions_answers_json",
            "final_target_id",
            "question_helpfulness_rating",
            "qualitative_feedback",
            "created_at",
        ]
        for col in expected_columns:
            assert col in columns, f"Column '{col}' missing from research_sessions table schema."


def test_temp_upload_directory_created_on_startup():
    """Verify configured TEMP_UPLOAD_DIR is created successfully during app startup."""
    assert os.path.exists(settings.TEMP_UPLOAD_DIR)
    assert os.path.isdir(settings.TEMP_UPLOAD_DIR)
