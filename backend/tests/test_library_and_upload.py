from __future__ import annotations
import os
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import session_manager, library_service, upload_service


from unittest.mock import patch
from app.services import gemini_client

@pytest.fixture
def client():
    session_manager.clear_all_sessions()
    with patch.object(gemini_client, "analyze_image", side_effect=gemini_client.GeminiAPIError("API mock")), \
         patch.object(gemini_client, "embed_text", return_value=[0.01] * 3072):
        with TestClient(app) as test_client:
            yield test_client
    session_manager.clear_all_sessions()


def create_tiny_image_bytes(format_type: str = "png") -> bytes:
    """Helper creating valid tiny image bytes."""
    if format_type.lower() in ("jpeg", "jpg"):
        # Minimal JPEG header + EOF
        return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \x22\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
    elif format_type.lower() == "webp":
        # Minimal RIFF WEBP bytes
        return b"RIFF\x1a\x00\x00\x00WEBPVP8 \x0e\x00\x00\x00P\x01\x00\x9d\x01\x2a\x01\x00\x01\x00\x02\x004\x25\xa4\x00"
    else:  # PNG
        return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-B\x00\x00\x00\x00IEND\xaeB`\x82"


def test_1_research_session_accepts_jpeg_upload(client):
    """1. Research session accepts JPEG upload."""
    session = session_manager.create_session(mode="research")
    img_bytes = create_tiny_image_bytes("jpeg")

    res = client.post(
        f"/api/v1/sessions/{session.session_id}/upload",
        files=[("files", ("test.jpg", io.BytesIO(img_bytes), "image/jpeg"))],
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload["data"]["uploadedCount"] == 1


def test_2_research_session_accepts_png_upload(client):
    """2. Research session accepts PNG."""
    session = session_manager.create_session(mode="research")
    img_bytes = create_tiny_image_bytes("png")

    res = client.post(
        f"/api/v1/sessions/{session.session_id}/upload",
        files=[("files", ("test.png", io.BytesIO(img_bytes), "image/png"))],
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload["data"]["uploadedCount"] == 1


def test_3_research_session_accepts_webp_upload(client):
    """3. Research session accepts WebP."""
    session = session_manager.create_session(mode="research")
    img_bytes = create_tiny_image_bytes("webp")

    res = client.post(
        f"/api/v1/sessions/{session.session_id}/upload",
        files=[("files", ("test.webp", io.BytesIO(img_bytes), "image/webp"))],
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload["data"]["uploadedCount"] == 1


def test_4_multiple_image_upload_succeeds(client):
    """4. Multiple image upload succeeds."""
    session = session_manager.create_session(mode="research")
    files = [
        ("files", (f"test_{i}.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))
        for i in range(5)
    ]

    res = client.post(f"/api/v1/sessions/{session.session_id}/upload", files=files)
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload["data"]["uploadedCount"] == 5
    assert payload["data"]["imageCount"] == 5


def test_5_more_than_30_images_rejected(client):
    """5. More than 30 images rejected."""
    session = session_manager.create_session(mode="research")
    files = [
        ("files", (f"test_{i}.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))
        for i in range(31)
    ]

    res = client.post(f"/api/v1/sessions/{session.session_id}/upload", files=files)
    assert res.status_code == 400
    payload = res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "MAX_IMAGE_LIMIT_EXCEEDED"


def test_6_file_greater_than_size_limit_rejected(client):
    """6. File > size limit rejected (10 MB cap)."""
    session = session_manager.create_session(mode="research")
    large_bytes = b"0" * (10 * 1024 * 1024 + 100)  # 10 MB + 100 bytes

    res = client.post(
        f"/api/v1/sessions/{session.session_id}/upload",
        files=[("files", ("huge.png", io.BytesIO(large_bytes), "image/png"))],
    )
    assert res.status_code == 400
    payload = res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "FILE_SIZE_EXCEEDED"


def test_7_unsupported_extension_rejected(client):
    """7. Unsupported extension rejected."""
    session = session_manager.create_session(mode="research")

    res = client.post(
        f"/api/v1/sessions/{session.session_id}/upload",
        files=[("files", ("document.pdf", io.BytesIO(b"dummy pdf bytes"), "image/png"))],
    )
    assert res.status_code == 400
    payload = res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "INVALID_FILE_EXTENSION"


def test_8_unsupported_mime_type_rejected(client):
    """8. Unsupported MIME type rejected."""
    session = session_manager.create_session(mode="research")

    res = client.post(
        f"/api/v1/sessions/{session.session_id}/upload",
        files=[("files", ("script.png", io.BytesIO(b"executable bytes"), "application/x-msdownload"))],
    )
    assert res.status_code == 400
    payload = res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "INVALID_MIME_TYPE"


def test_9_empty_image_rejected(client):
    """9. Empty image rejected (0 bytes)."""
    session = session_manager.create_session(mode="research")

    res = client.post(
        f"/api/v1/sessions/{session.session_id}/upload",
        files=[("files", ("empty.png", io.BytesIO(b""), "image/png"))],
    )
    assert res.status_code == 400
    payload = res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "EMPTY_FILE_REJECTED"


def test_10_demo_session_upload_rejected(client):
    """10. Demo session upload rejected."""
    session = session_manager.create_session(mode="demo")

    res = client.post(
        f"/api/v1/sessions/{session.session_id}/upload",
        files=[("files", ("test.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )
    assert res.status_code == 400
    payload = res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "UPLOAD_NOT_ALLOWED_IN_DEMO_MODE"


def test_11_invalid_session_id_rejected(client):
    """11. Invalid session ID rejected."""
    res = client.post(
        "/api/v1/sessions/non_existent_session/upload",
        files=[("files", ("test.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )
    assert res.status_code == 404
    payload = res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "SESSION_NOT_FOUND"


def test_12_uploaded_files_saved_under_correct_session_directory(client):
    """12. Uploaded files saved under correct session directory (TEMP_UPLOAD_DIR/{session_id}/)."""
    session = session_manager.create_session(mode="research")
    res = client.post(
        f"/api/v1/sessions/{session.session_id}/upload",
        files=[("files", ("photo.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )
    assert res.status_code == 200

    session_dir = upload_service.get_session_upload_dir(session.session_id)
    assert os.path.exists(session_dir)
    saved_files = os.listdir(session_dir)
    assert len(saved_files) == 1
    assert saved_files[0].startswith("research_")


def test_13_two_research_sessions_remain_isolated(client):
    """13. Two research sessions remain isolated."""
    s1 = session_manager.create_session(mode="research")
    s2 = session_manager.create_session(mode="research")

    client.post(
        f"/api/v1/sessions/{s1.session_id}/upload",
        files=[("files", ("photo1.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )
    client.post(
        f"/api/v1/sessions/{s2.session_id}/upload",
        files=[("files", ("photo2.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )

    lib1 = library_service.get_research_library(s1.session_id)
    lib2 = library_service.get_research_library(s2.session_id)

    assert len(lib1) == 1
    assert len(lib2) == 1
    assert lib1[0].image_id != lib2[0].image_id
    assert lib1[0].session_id == s1.session_id
    assert lib2[0].session_id == s2.session_id


def test_14_session_a_cannot_fetch_session_b_image(client):
    """14. Session A cannot fetch Session B image."""
    s1 = session_manager.create_session(mode="research")
    s2 = session_manager.create_session(mode="research")

    res = client.post(
        f"/api/v1/sessions/{s1.session_id}/upload",
        files=[("files", ("photo1.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )
    img_id1 = library_service.get_research_library(s1.session_id)[0].image_id

    # Session 2 tries to fetch Session 1's image
    fetch_res = client.get(f"/api/v1/sessions/{s2.session_id}/images/{img_id1}")
    assert fetch_res.status_code == 404
    payload = fetch_res.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "IMAGE_NOT_FOUND"


def test_15_path_traversal_attempt_rejected(client):
    """15. Path traversal attempt rejected."""
    s1 = session_manager.create_session(mode="research")
    res = client.get(f"/api/v1/sessions/{s1.session_id}/images/..%2F..%2Fetc%2Fpasswd")
    assert res.status_code == 404


def test_16_cleanup_research_session_files_deletes_only_correct_directory(client):
    """16. cleanup_research_session_files deletes only correct session directory."""
    s1 = session_manager.create_session(mode="research")
    s2 = session_manager.create_session(mode="research")

    client.post(
        f"/api/v1/sessions/{s1.session_id}/upload",
        files=[("files", ("p1.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )
    client.post(
        f"/api/v1/sessions/{s2.session_id}/upload",
        files=[("files", ("p2.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )

    dir1 = upload_service.get_session_upload_dir(s1.session_id)
    dir2 = upload_service.get_session_upload_dir(s2.session_id)

    assert os.path.exists(dir1)
    assert os.path.exists(dir2)

    upload_service.cleanup_research_session_files(s1.session_id)

    assert not os.path.exists(dir1)
    assert os.path.exists(dir2)  # Session 2 directory untouched!


def test_17_cleanup_called_twice_does_not_crash(client):
    """17. Cleanup called twice does not crash."""
    s1 = session_manager.create_session(mode="research")
    client.post(
        f"/api/v1/sessions/{s1.session_id}/upload",
        files=[("files", ("p1.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )

    upload_service.cleanup_research_session_files(s1.session_id)
    # Second cleanup call should return gracefully
    upload_service.cleanup_research_session_files(s1.session_id)


def test_18_terminal_research_session_cleanup_works(client):
    """18. Terminal research session cleanup works (mark_found, delete_session)."""
    s1 = session_manager.create_session(mode="research")
    client.post(
        f"/api/v1/sessions/{s1.session_id}/upload",
        files=[("files", ("p1.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )
    dir1 = upload_service.get_session_upload_dir(s1.session_id)
    assert os.path.exists(dir1)

    # Mark found triggers automatic file cleanup
    session_manager.mark_found(s1.session_id, final_target_id="img_001")
    assert not os.path.exists(dir1)


def test_19_demo_manifest_loads(client):
    """19. Demo manifest loads."""
    manifest = library_service.load_demo_manifest()
    assert len(manifest) > 0
    assert manifest[0].source == "demo"
    assert manifest[0].image_id.startswith("demo_")


def test_20_demo_library_count_is_correct(client):
    """20. Demo library count is correct (29 images)."""
    session = session_manager.create_session(mode="demo")
    count = library_service.get_library_image_count(session.session_id)
    assert count == 29


def test_21_standard_api_envelope_used_for_success_and_errors(client):
    """21. Standard API envelope used for success/errors."""
    s = session_manager.create_session(mode="research")

    # Success envelope
    succ_res = client.post(
        f"/api/v1/sessions/{s.session_id}/upload",
        files=[("files", ("valid.png", io.BytesIO(create_tiny_image_bytes("png")), "image/png"))],
    )
    succ_json = succ_res.json()
    assert "success" in succ_json and succ_json["success"] is True
    assert "data" in succ_json and succ_json["data"] is not None
    assert "error" in succ_json and succ_json["error"] is None

    # Error envelope
    err_res = client.post(
        f"/api/v1/sessions/{s.session_id}/upload",
        files=[("files", ("bad.exe", io.BytesIO(b"executable"), "application/x-msdownload"))],
    )
    err_json = err_res.json()
    assert "success" in err_json and err_json["success"] is False
    assert "data" in err_json and err_json["data"] is None
    assert "error" in err_json and "code" in err_json["error"] and "message" in err_json["error"]
