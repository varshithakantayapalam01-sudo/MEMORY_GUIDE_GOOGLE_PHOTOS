from __future__ import annotations
import io
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.services import (
    gemini_client,
    session_manager,
    upload_service,
    image_understanding_service,
    library_service,
)
from app.models.image import ImageProfile

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_test_sessions():
    yield
    session_manager.clear_all_sessions()


def test_build_and_validate_image_profile_complete():
    raw_dict = {
        "people_count": "2",
        "people_age_group": ["adult"],
        "people_description": "Two friends sitting",
        "setting": "indoor",
        "setting_type": "living room",
        "setting_details": "cozy couch with pillows",
        "time_of_day": "day",
        "season_hint": "unclear",
        "activity": "celebrating",
        "occasion": "birthday",
        "clothing": ["blue shirt", "white dress"],
        "objects": ["cake", "balloons"],
        "animals": [],
        "dominant_colors": ["blue", "white"],
        "mood": "happy",
        "composition": "group",
        "free_description": "Two friends celebrating a birthday indoors with cake.",
    }

    profile = image_understanding_service.build_and_validate_image_profile(
        image_id="img_test_1",
        raw_dict=raw_dict,
        file_path="/tmp/img_test_1.jpg",
        image_url="/images/img_test_1.jpg",
        identity_tags=["sister"],
    )

    assert profile.image_id == "img_test_1"
    assert profile.setting == "indoor"
    assert profile.activity == "celebrating"
    assert profile.dominant_colors == ["blue", "white"]
    assert profile.identity_tags == ["sister"]
    assert profile.profile_status == "complete"
    assert len(profile.profile_warnings) == 0


def test_build_and_validate_image_profile_partial_and_failed():
    raw_dict_partial = {
        "setting": "outdoor",
        "objects": ["bench"],
        # Missing activity/occasion, dominant_colors, free_description
    }

    profile_partial = image_understanding_service.build_and_validate_image_profile(
        image_id="img_partial",
        raw_dict=raw_dict_partial,
    )

    assert profile_partial.profile_status in ("partial", "failed")
    assert len(profile_partial.profile_warnings) > 0

    profile_failed = image_understanding_service.build_and_validate_image_profile(
        image_id="img_failed",
        raw_dict={},
    )
    assert profile_failed.profile_status == "failed"
    assert "empty or invalid" in profile_failed.profile_warnings[0].lower()


def test_identity_tags_never_injected_by_gemini():
    raw_dict_with_fake_tags = {
        "setting": "indoor",
        "activity": "eating",
        "dominant_colors": ["red"],
        "free_description": "Eating lunch",
        "identity_tags": ["injected_sister_name"],  # Attempt to inject via Gemini dict
    }

    profile = image_understanding_service.build_and_validate_image_profile(
        image_id="img_no_tag",
        raw_dict=raw_dict_with_fake_tags,
        identity_tags=None,
    )

    assert profile.identity_tags == []


def test_gemini_client_success():
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "setting": "indoor",
        "activity": "celebrating",
        "dominant_colors": ["red", "gold"],
        "free_description": "Festive indoor gathering."
    })

    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with patch.object(settings, "GEMINI_API_KEY", "AIzaSyTestKey123"):
            res = gemini_client.analyze_image(b"fake_image_bytes", mime_type="image/jpeg")
            assert res["setting"] == "indoor"
            assert res["activity"] == "celebrating"


def test_gemini_client_parse_error():
    mock_response = MagicMock()
    mock_response.text = "NOT JSON TEXT AT ALL"

    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with patch.object(settings, "GEMINI_API_KEY", "AIzaSyTestKey123"):
            with pytest.raises(gemini_client.GeminiParseError):
                gemini_client.analyze_image(b"fake_image_bytes", max_retries=0)


def test_load_demo_profiles():
    profiles = image_understanding_service.load_demo_profiles()
    assert isinstance(profiles, dict)
    assert len(profiles) > 0
    assert "demo_001" in profiles
    assert profiles["demo_001"].setting is not None


def test_index_research_library_mocked():
    session = session_manager.create_session(mode="research")

    # Upload mock image
    fake_img = io.BytesIO(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00")
    response = client.post(
        f"/api/v1/sessions/{session.session_id}/upload",
        files=[("files", ("test_photo.jpg", fake_img, "image/jpeg"))],
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["uploadedCount"] == 1
    assert data["status"] == "ready"

    # Verify session retrieval status transitioned to ready
    updated_session = session_manager.get_session(session.session_id)
    assert updated_session.retrieval_status == "ready"

    # Check that profile exists
    profs = image_understanding_service.get_session_profiles(session.session_id)
    assert len(profs) == 1
    assert profs[0].image_id.startswith("res_")


def test_get_image_profile_isolation():
    demo_session = session_manager.create_session(mode="demo")
    res_session_1 = session_manager.create_session(mode="research")
    res_session_2 = session_manager.create_session(mode="research")

    # Demo session can get demo profiles
    demo_prof = image_understanding_service.get_image_profile(demo_session.session_id, "demo_001")
    assert demo_prof is not None
    assert demo_prof.image_id == "demo_001"

    # Research session 1 cannot get demo profile via get_image_profile
    assert image_understanding_service.get_image_profile(res_session_1.session_id, "demo_001") is None

    # Upload photo to research session 1
    fake_img = io.BytesIO(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00")
    client.post(
        f"/api/v1/sessions/{res_session_1.session_id}/upload",
        files=[("files", ("res1_photo.jpg", fake_img, "image/jpeg"))],
    )

    res1_profs = image_understanding_service.get_session_profiles(res_session_1.session_id)
    assert len(res1_profs) == 1
    res1_img_id = res1_profs[0].image_id

    # Research session 1 can access its own profile
    assert image_understanding_service.get_image_profile(res_session_1.session_id, res1_img_id) is not None

    # Research session 2 CANNOT access research session 1's profile
    assert image_understanding_service.get_image_profile(res_session_2.session_id, res1_img_id) is None


def test_debug_profiles_endpoint():
    demo_session = session_manager.create_session(mode="demo")

    res = client.get(f"/api/v1/sessions/{demo_session.session_id}/profiles")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["data"]["mode"] == "demo"
    assert json_data["data"]["profileCount"] > 0
    assert len(json_data["data"]["profiles"]) > 0

    # Non-existent session
    res_404 = client.get("/api/v1/sessions/non_existent_id/profiles")
    assert res_404.status_code == 404
