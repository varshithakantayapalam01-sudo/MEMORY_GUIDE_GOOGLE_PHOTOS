from __future__ import annotations
import os
import json
import logging
from typing import Dict, List, Optional
from app.config import settings
from app.models.image import ImageProfile
from app.services import gemini_client, session_manager, image_understanding_service
from app.services.search_document import build_search_document
from scripts.generate_demo_embeddings import generate_deterministic_synthetic_vector

logger = logging.getLogger("memory_guide.embedding_service")

DEMO_EMBEDDINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "demo_embeddings.json")

# In-memory store for research embeddings: session_id -> {image_id: list[float]}
_research_embeddings: Dict[str, Dict[str, List[float]]] = {}

# In-memory cache for demo embeddings
_demo_embeddings_cache: Optional[Dict[str, List[float]]] = None


def load_demo_embeddings(force_reload: bool = False) -> Dict[str, List[float]]:
    """
    Loads precomputed demo embeddings from demo_embeddings.json.
    """
    global _demo_embeddings_cache
    if _demo_embeddings_cache is not None and not force_reload:
        return _demo_embeddings_cache

    path = os.path.abspath(DEMO_EMBEDDINGS_PATH)
    if not os.path.exists(path):
        logger.warning(f"Demo embeddings file not found at {path}")
        _demo_embeddings_cache = {}
        return _demo_embeddings_cache

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        embeddings = {}
        for item in data:
            image_id = item["image_id"]
            embeddings[image_id] = item["embedding"]

        _demo_embeddings_cache = embeddings
        return embeddings
    except Exception as e:
        logger.error(f"Failed to load demo embeddings: {e}")
        _demo_embeddings_cache = {}
        return _demo_embeddings_cache


def index_research_embeddings(session_id: str) -> bool:
    """
    Generates semantic vector embeddings for a Research Mode session's image profiles.
    Stores embeddings in memory strictly scoped to session_id.
    """
    session = session_manager.get_session(session_id)
    if not session or session.mode != "research":
        return False

    profiles = image_understanding_service.get_session_profiles(session_id)
    has_api_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key")

    session_embs: Dict[str, List[float]] = {}
    for prof in profiles:
        doc = build_search_document(prof)
        vector = None
        if has_api_key:
            try:
                vector = gemini_client.embed_text(doc)
            except Exception as e:
                logger.warning(f"Gemini embedding failed for research photo {prof.image_id}: {e}")

        if not vector:
            if not settings.ALLOW_SYNTHETIC_AI:
                raise gemini_client.GeminiAPIError(
                    f"Gemini embedding failed for research photo {prof.image_id} and synthetic fallback is disabled (ALLOW_SYNTHETIC_AI=false)."
                )
            vector = generate_deterministic_synthetic_vector(doc)

        session_embs[prof.image_id] = vector

    _research_embeddings[session_id] = session_embs
    logger.info(f"Generated embeddings for {len(session_embs)} research photos in session {session_id}.")
    return True


def get_session_embeddings(session_id: str) -> Dict[str, List[float]]:
    """
    Returns image embeddings for a session based on mode.
    ENFORCES STRICT SESSION ISOLATION.
    """
    session = session_manager.get_session(session_id)
    if not session:
        return {}

    if session.mode == "demo":
        return load_demo_embeddings()

    elif session.mode == "research":
        # If embeddings not yet indexed for research session, index now
        if session_id not in _research_embeddings:
            index_research_embeddings(session_id)
        return _research_embeddings.get(session_id, {})

    return {}


def clear_research_embeddings(session_id: str) -> None:
    """
    Clears research embeddings from memory during session cleanup.
    """
    if session_id in _research_embeddings:
        del _research_embeddings[session_id]
