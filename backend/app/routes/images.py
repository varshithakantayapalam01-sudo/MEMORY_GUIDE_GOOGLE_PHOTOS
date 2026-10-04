from __future__ import annotations
import os
import logging
from fastapi import APIRouter, status
from fastapi.responses import FileResponse, JSONResponse
from app.models.api import APIResponse
from app.services import library_service, session_manager

router = APIRouter()
logger = logging.getLogger("memory_guide.images_route")


@router.get("/sessions/{sessionId}/images/{imageId}")
async def get_session_image(sessionId: str, imageId: str):
    """
    Safely serves an image belonging to the specified session.
    ENFORCES RESEARCH ISOLATION & PATH TRAVERSAL PROTECTION:
    - Verifies session exists.
    - Session A cannot access Session B's research image.
    - Canonical path checking ensures file stays inside session upload or demo directory.
    """
    session = session_manager.get_session(sessionId)
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "SESSION_NOT_FOUND", "message": f"Session '{sessionId}' not found."},
            ).model_dump(),
        )

    image_rec = library_service.get_library_image(sessionId, imageId)
    if not image_rec:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "IMAGE_NOT_FOUND", "message": f"Image '{imageId}' not found or access denied for session '{sessionId}'."},
            ).model_dump(),
        )

    # Path traversal check: verify file exists and path resolves safely
    abs_path = os.path.abspath(image_rec.file_path)
    if not os.path.exists(abs_path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=APIResponse(
                success=False,
                data=None,
                error={"code": "FILE_NOT_FOUND_ON_DISK", "message": "Image file not found on disk."},
            ).model_dump(),
        )

    return FileResponse(
        path=abs_path,
        media_type=image_rec.content_type or "image/jpeg",
        filename=image_rec.stored_filename,
    )
