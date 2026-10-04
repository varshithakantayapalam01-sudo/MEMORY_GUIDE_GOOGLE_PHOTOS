from __future__ import annotations
import os
import shutil
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Tuple
from fastapi import UploadFile
from app.config import settings
from app.models.library import LibraryImage
from app.services import session_manager, library_service

logger = logging.getLogger("memory_guide.upload_service")

# Validation Constants
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/pjpeg",
    "image/png",
    "image/x-png",
    "image/webp",
    "image/heic",
    "image/heif",
    "application/octet-stream",
    "",
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit per image
MAX_IMAGES_PER_SESSION = 30


class UploadValidationError(Exception):
    """Exception raised when an uploaded file fails validation."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def get_session_upload_dir(session_id: str) -> str:
    """
    Returns the isolated upload directory path for a research session:
    TEMP_UPLOAD_DIR/{session_id}/
    """
    base_dir = os.path.abspath(settings.TEMP_UPLOAD_DIR)
    session_dir = os.path.abspath(os.path.join(base_dir, session_id))

    # Path traversal protection: ensure session_dir is strictly inside base_dir
    if not session_dir.startswith(base_dir + os.sep) and session_dir != base_dir:
        raise UploadValidationError("PATH_TRAVERSAL_DETECTED", "Invalid session directory path.")

    return session_dir


def validate_file(file: UploadFile, current_count: int, total_batch_count: int) -> Tuple[str, str]:
    """
    Validates extension, MIME type, file size, non-emptiness, and count limits.
    Returns (sanitized_extension, content_type).
    """
    if current_count + total_batch_count > MAX_IMAGES_PER_SESSION:
        raise UploadValidationError(
            "MAX_IMAGE_LIMIT_EXCEEDED",
            f"Maximum image limit of {MAX_IMAGES_PER_SESSION} images per research session exceeded."
        )

    # 1. Filename & extension check
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    # Default fallback if extension missing
    if not ext:
        if "png" in (file.content_type or ""):
            ext = ".png"
        elif "webp" in (file.content_type or ""):
            ext = ".webp"
        else:
            ext = ".jpg"

    if ext not in ALLOWED_EXTENSIONS:
        raise UploadValidationError(
            "INVALID_FILE_EXTENSION",
            f"File format '{ext}' is not supported. Allowed formats: JPG, JPEG, PNG, WebP, HEIC."
        )

    # 2. Content-Type check & normalization
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_MIME_TYPES and not content_type.startswith("image/"):
        raise UploadValidationError(
            "INVALID_MIME_TYPE",
            f"MIME type '{content_type}' is not supported. Please upload a standard image file."
        )

    # Normalize content_type for serving
    if not content_type or content_type == "application/octet-stream" or content_type == "image/jpg" or content_type == "image/pjpeg":
        if ext in {".png"}:
            content_type = "image/png"
        elif ext in {".webp"}:
            content_type = "image/webp"
        else:
            content_type = "image/jpeg"

    return ext, content_type


async def save_research_uploads(session_id: str, files: List[UploadFile]) -> List[LibraryImage]:
    """
    Saves a batch of research upload files into the session-isolated directory.
    Validates every file and assigns safe server-generated filenames.
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise UploadValidationError("SESSION_NOT_FOUND", f"Session '{session_id}' not found.")

    if session.mode != "research":
        raise UploadValidationError(
            "UPLOAD_NOT_ALLOWED_IN_DEMO_MODE",
            "Photo uploads are only permitted in Research Mode sessions."
        )

    if not files:
        raise UploadValidationError("EMPTY_UPLOAD_BATCH", "No files provided in upload request.")

    existing_library = library_service.get_research_library(session_id)
    current_count = len(existing_library)

    if current_count + len(files) > MAX_IMAGES_PER_SESSION:
        raise UploadValidationError(
            "MAX_IMAGE_LIMIT_EXCEEDED",
            f"Cannot upload {len(files)} photos. Session already has {current_count} photos (max {MAX_IMAGES_PER_SESSION})."
        )

    session_dir = get_session_upload_dir(session_id)
    os.makedirs(session_dir, exist_ok=True)

    saved_images: List[LibraryImage] = []

    for i, file in enumerate(files, start=1):
        ext, content_type = validate_file(file, current_count, len(files))

        # Read file contents and check size
        contents = await file.read()
        file_size = len(contents)

        if file_size == 0:
            raise UploadValidationError("EMPTY_FILE_REJECTED", f"Uploaded file '{file.filename}' is empty (0 bytes).")

        if file_size > MAX_FILE_SIZE_BYTES:
            raise UploadValidationError(
                "FILE_SIZE_EXCEEDED",
                f"File '{file.filename}' exceeds maximum allowed size of 10 MB ({file_size} bytes)."
            )

        # Generate safe server-controlled filename and image_id
        img_number = current_count + i
        stored_filename = f"research_{img_number:04d}{ext}"
        file_path = os.path.join(session_dir, stored_filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        image_id = f"res_img_{session_id[-6:]}_{img_number:04d}"
        image_url = f"/api/v1/sessions/{session_id}/images/{image_id}"

        lib_img = LibraryImage(
            image_id=image_id,
            session_id=session_id,
            source="research",
            stored_filename=stored_filename,
            file_path=os.path.abspath(file_path),
            image_url=image_url,
            content_type=content_type,
            file_size=file_size,
        )
        saved_images.append(lib_img)

    # Register saved images with library service
    library_service.register_research_images(session_id, saved_images)
    return saved_images


def cleanup_research_session_files(session_id: str) -> bool:
    """
    Deletes the session-isolated temporary upload directory and clears memory records.
    Safely handles already-deleted directories without crashing.
    """
    library_service.clear_research_library(session_id)

    try:
        session_dir = get_session_upload_dir(session_id)
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir, ignore_errors=True)
            logger.info(f"Cleaned up research upload directory for session '{session_id}'.")
            return True
    except Exception as e:
        logger.error(f"Error cleaning up files for session '{session_id}': {e}")

    return False


def cleanup_expired_research_sessions(inactivity_hours: float = 2.0) -> int:
    """
    MVP Expiration Cleanup: Scans temporary upload directory for session directories
    older than inactivity_hours and deletes them.
    Returns count of cleaned up session directories.
    """
    base_dir = os.path.abspath(settings.TEMP_UPLOAD_DIR)
    if not os.path.exists(base_dir):
        return 0

    cleaned_count = 0
    now = datetime.now(timezone.utc)
    threshold = timedelta(hours=inactivity_hours)

    try:
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                # Check directory modification time
                mtime = datetime.fromtimestamp(os.path.getmtime(item_path), tz=timezone.utc)
                if now - mtime > threshold:
                    shutil.rmtree(item_path, ignore_errors=True)
                    library_service.clear_research_library(item)
                    cleaned_count += 1
                    logger.info(f"Cleaned up expired research session directory: {item}")
    except Exception as e:
        logger.error(f"Error during expired research session cleanup: {e}")

    return cleaned_count
