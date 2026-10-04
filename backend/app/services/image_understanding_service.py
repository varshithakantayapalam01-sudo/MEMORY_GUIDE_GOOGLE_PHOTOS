from __future__ import annotations
import os
import json
import logging
from typing import Dict, List, Optional, Any
from app.config import settings
from app.models.image import ImageProfile
from app.services import gemini_client, library_service, session_manager

logger = logging.getLogger("memory_guide.image_understanding")

DEMO_PROFILES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "demo_profiles.json")

# In-memory storage for research profiles: session_id -> {image_id: ImageProfile}
_research_profiles: Dict[str, Dict[str, ImageProfile]] = {}

# In-memory cache for demo profiles
_demo_profiles_cache: Optional[Dict[str, ImageProfile]] = None


def build_and_validate_image_profile(
    image_id: str,
    raw_dict: dict[str, Any],
    file_path: Optional[str] = None,
    image_url: Optional[str] = None,
    identity_tags: Optional[List[str]] = None,
) -> ImageProfile:
    """
    Validates raw extracted attributes dictionary from Gemini or fallback into a strict ImageProfile model.
    Populates profile_status ('complete' | 'partial' | 'failed') and profile_warnings.
    NEVER allows Gemini output to inject identity_tags.
    """
    warnings: List[str] = []

    if not raw_dict or not isinstance(raw_dict, dict):
        return ImageProfile(
            image_id=image_id,
            file_path=file_path,
            image_url=image_url,
            identity_tags=identity_tags or [],
            profile_status="failed",
            profile_warnings=["Raw extraction output was empty or invalid dict."],
        )

    def _clean_str(val: Any) -> Optional[str]:
        if val is None or val == "" or str(val).lower() in ("unclear", "none", "null", "unknown"):
            return None
        return str(val).strip()

    def _clean_list(val: Any) -> List[str]:
        if not val or not isinstance(val, list):
            return []
        cleaned = []
        for item in val:
            s = _clean_str(item)
            if s:
                cleaned.append(s)
        return cleaned

    people_count = _clean_str(raw_dict.get("people_count"))
    people_age_group = _clean_list(raw_dict.get("people_age_group"))
    people_description = _clean_str(raw_dict.get("people_description"))

    setting = _clean_str(raw_dict.get("setting"))
    setting_type = _clean_str(raw_dict.get("setting_type"))
    setting_details = _clean_str(raw_dict.get("setting_details"))

    time_of_day = _clean_str(raw_dict.get("time_of_day"))
    season_hint = _clean_str(raw_dict.get("season_hint"))

    activity = _clean_str(raw_dict.get("activity"))
    occasion = _clean_str(raw_dict.get("occasion"))

    clothing = _clean_list(raw_dict.get("clothing"))
    objects = _clean_list(raw_dict.get("objects"))
    animals = _clean_list(raw_dict.get("animals"))
    dominant_colors = _clean_list(raw_dict.get("dominant_colors"))

    mood = _clean_str(raw_dict.get("mood"))
    composition = _clean_str(raw_dict.get("composition"))
    free_description = _clean_str(raw_dict.get("free_description"))

    # Determine status & warnings
    missing_fields = []
    if not setting:
        missing_fields.append("setting")
    if not activity and not occasion:
        missing_fields.append("activity/occasion")
    if not dominant_colors:
        missing_fields.append("dominant_colors")
    if not free_description:
        missing_fields.append("free_description")

    if missing_fields:
        warnings.append(f"Missing or unclear key attributes: {', '.join(missing_fields)}")

    if len(missing_fields) >= 3:
        status = "failed"
    elif missing_fields:
        status = "partial"
    else:
        status = "complete"

    return ImageProfile(
        image_id=image_id,
        image_url=image_url,
        file_path=file_path,
        people_count=people_count,
        people_age_group=people_age_group,
        people_description=people_description,
        setting=setting,
        setting_type=setting_type,
        setting_details=setting_details,
        time_of_day=time_of_day,
        season_hint=season_hint,
        activity=activity,
        occasion=occasion,
        clothing=clothing,
        objects=objects,
        animals=animals,
        dominant_colors=dominant_colors,
        mood=mood,
        composition=composition,
        free_description=free_description,
        identity_tags=identity_tags or [],
        profile_status=status,
        profile_warnings=warnings,
    )


def load_demo_profiles(force_reload: bool = False) -> Dict[str, ImageProfile]:
    """
    Loads precomputed demo image profiles from demo_profiles.json.
    Cached in memory.
    """
    global _demo_profiles_cache
    if _demo_profiles_cache is not None and not force_reload:
        return _demo_profiles_cache

    profiles_path = os.path.abspath(DEMO_PROFILES_PATH)
    if not os.path.exists(profiles_path):
        logger.warning(f"Demo profiles file not found at {profiles_path}")
        _demo_profiles_cache = {}
        return _demo_profiles_cache

    try:
        with open(profiles_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        profiles = {}
        for item in data:
            image_id = item["image_id"]
            prof = ImageProfile(**item)
            profiles[image_id] = prof

        _demo_profiles_cache = profiles
        return profiles
    except Exception as e:
        logger.error(f"Failed to load demo profiles: {e}")
        _demo_profiles_cache = {}
        return _demo_profiles_cache


def index_research_library(session_id: str) -> bool:
    """
    Indexes all uploaded research images for a session using Gemini Vision (or fallback).
    Transitions retrieval_status: created -> indexing -> ready.
    Stores resulting ImageProfiles in memory strictly scoped to session_id.
    """
    session = session_manager.get_session(session_id)
    if not session or session.mode != "research":
        return False

    session.retrieval_status = "indexing"
    images = library_service.get_research_library(session_id)
    session_profiles: Dict[str, ImageProfile] = {}

    for img in images:
        raw_dict = {}
        fallback_warning = None

        if img.file_path and os.path.exists(img.file_path):
            has_api_key = bool(
                settings.GEMINI_API_KEY
                and settings.GEMINI_API_KEY != "your_gemini_api_key"
            )
            if has_api_key:
                try:
                    with open(img.file_path, "rb") as f:
                        image_bytes = f.read()

                    raw_dict = gemini_client.analyze_image(
                        image_bytes=image_bytes,
                        mime_type=img.content_type or "image/jpeg",
                    )
                except Exception as e:
                    logger.warning(f"Gemini analysis failed for research photo {img.image_id}: {e}")
                    fallback_warning = f"Gemini analysis fallback used: {e}"
                    raw_dict = {
                        "setting": "unclear",
                        "free_description": f"Uploaded photo ({img.stored_filename})",
                        "dominant_colors": ["unclear"],
                    }
            else:
                fallback_warning = "Gemini API key not configured. Using fallback metadata extraction."
                raw_dict = {
                    "setting": "unclear",
                    "free_description": f"Uploaded photo ({img.stored_filename})",
                    "dominant_colors": ["unclear"],
                }
        else:
            fallback_warning = "Image file not found on server disk."
            raw_dict = {
                "setting": "unclear",
                "free_description": "Missing file profile fallback.",
            }

        profile = build_and_validate_image_profile(
            image_id=img.image_id,
            raw_dict=raw_dict,
            file_path=img.file_path,
            image_url=img.image_url,
            identity_tags=[],  # Research photos have no pre-tagged identities
        )

        if fallback_warning:
            profile.profile_warnings.append(fallback_warning)
            if profile.profile_status == "complete":
                profile.profile_status = "partial"

        session_profiles[img.image_id] = profile

    _research_profiles[session_id] = session_profiles
    session.retrieval_status = "ready"
    logger.info(f"Research library indexing complete for session {session_id} ({len(session_profiles)} profiles).")
    return True


def get_image_profile(session_id: str, image_id: str) -> Optional[ImageProfile]:
    """
    Retrieves the ImageProfile for an image in the given session.
    ENFORCES STRICT SESSION ISOLATION:
    - Demo mode -> returns profile from demo_profiles.json
    - Research mode -> returns profile ONLY if image_id belongs to session_id's research profiles
    """
    session = session_manager.get_session(session_id)
    if not session:
        return None

    if session.mode == "demo":
        demo_profs = load_demo_profiles()
        return demo_profs.get(image_id)

    elif session.mode == "research":
        res_profs = _research_profiles.get(session_id, {})
        return res_profs.get(image_id)

    return None


def get_session_profiles(session_id: str) -> List[ImageProfile]:
    """
    Returns all ImageProfiles for the session's library.
    ENFORCES STRICT SESSION ISOLATION.
    """
    session = session_manager.get_session(session_id)
    if not session:
        return []

    if session.mode == "demo":
        demo_profs = load_demo_profiles()
        return list(demo_profs.values())

    elif session.mode == "research":
        res_profs = _research_profiles.get(session_id, {})
        return list(res_profs.values())

    return []


def clear_research_profiles(session_id: str) -> None:
    """
    Clears in-memory research profiles for a session upon termination/cleanup.
    """
    if session_id in _research_profiles:
        del _research_profiles[session_id]
