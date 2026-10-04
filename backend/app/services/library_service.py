from __future__ import annotations
import os
import json
import logging
from typing import Optional, List, Dict
from app.models.library import LibraryImage
from app.services import session_manager

logger = logging.getLogger("memory_guide.library_service")

# Path to demo manifest
DEMO_MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "demo_library.json")
DEMO_PHOTOS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "demo-photos")

# In-memory registry for research libraries per session
# session_id -> list[LibraryImage]
_research_libraries: Dict[str, List[LibraryImage]] = {}


def load_demo_manifest() -> List[LibraryImage]:
    """
    Loads the demo library manifest JSON file and returns a list of LibraryImage objects.
    """
    manifest_path = os.path.abspath(DEMO_MANIFEST_PATH)
    if not os.path.exists(manifest_path):
        logger.warning(f"Demo manifest file not found at {manifest_path}")
        return []

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        images = []
        for item in data:
            filename = item.get("filename", "")
            file_path = os.path.abspath(os.path.join(DEMO_PHOTOS_DIR, filename))
            img = LibraryImage(
                image_id=item["image_id"],
                session_id=None,
                source="demo",
                stored_filename=filename,
                file_path=file_path,
                image_url=item.get("image_url", f"/images/demo-photos/{filename}"),
                content_type="image/jpeg",
                file_size=os.path.getsize(file_path) if os.path.exists(file_path) else None,
                cluster_id=item.get("cluster_id"),
                manual_label=item.get("manual_label"),
            )
            images.append(img)
        return images
    except Exception as e:
        logger.error(f"Error loading demo manifest: {e}")
        return []


def get_demo_library() -> List[LibraryImage]:
    """
    Returns all globally available demo library images.
    """
    return load_demo_manifest()


def get_research_library(session_id: str) -> List[LibraryImage]:
    """
    Returns research images belonging to the specified session.
    Never returns another session's research images.
    """
    return _research_libraries.get(session_id, [])


def register_research_images(session_id: str, images: List[LibraryImage]) -> None:
    """
    Registers research images for a session.
    """
    if session_id not in _research_libraries:
        _research_libraries[session_id] = []
    _research_libraries[session_id].extend(images)


def clear_research_library(session_id: str) -> None:
    """
    Clears research image records for a session from memory.
    """
    if session_id in _research_libraries:
        del _research_libraries[session_id]


def get_library(session_id: str) -> List[LibraryImage]:
    """
    Resolves the correct library for a session based on session mode.
    - demo mode -> demo library
    - research mode -> session-isolated research library
    """
    session = session_manager.get_session(session_id)
    if not session:
        return []

    if session.mode == "demo":
        return get_demo_library()
    elif session.mode == "research":
        return get_research_library(session_id)
    return []


def get_library_image_count(session_id: str) -> int:
    """
    Returns the total number of images available in the session's library.
    """
    return len(get_library(session_id))


def get_library_image(session_id: str, image_id: str) -> Optional[LibraryImage]:
    """
    Retrieves a single image from the session's library.
    ENFORCES RESEARCH ISOLATION:
    - In research mode, ONLY returns the image if it belongs to session_id.
    - Demo images are read-only and globally accessible across sessions.
    """
    session = session_manager.get_session(session_id)
    if not session:
        return None

    if session.mode == "demo":
        for img in get_demo_library():
            if img.image_id == image_id:
                return img
        return None

    elif session.mode == "research":
        research_imgs = get_research_library(session_id)
        for img in research_imgs:
            if img.image_id == image_id:
                return img
        return None

    return None
