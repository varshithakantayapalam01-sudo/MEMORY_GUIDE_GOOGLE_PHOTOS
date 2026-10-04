from __future__ import annotations
import os
import sys
import json
import logging
from datetime import datetime, timezone

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.models.image import ImageProfile
from app.services import gemini_client
from app.services.search_document import build_search_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generate_demo_embeddings")

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "data"))
PROFILES_PATH = os.path.join(DATA_DIR, "demo_profiles.json")
OUTPUT_EMBEDDINGS_PATH = os.path.join(DATA_DIR, "demo_embeddings.json")


def generate_deterministic_synthetic_vector(text: str, dim: int = 768) -> list[float]:
    """
    Generates a deterministic unit-norm float vector based on text content hash
    when live GEMINI_API_KEY is not configured.
    """
    import hashlib
    import math

    vector = []
    for i in range(dim):
        seed = f"{text}_{i}".encode("utf-8")
        h = hashlib.sha256(seed).digest()
        val = (int.from_bytes(h[:4], "big") / (2**32 - 1)) * 2.0 - 1.0
        vector.append(val)

    norm = math.sqrt(sum(v * v for v in vector))
    return [v / norm for v in vector] if norm > 0 else vector


def main(force_regenerate: bool = False):
    if not os.path.exists(PROFILES_PATH):
        logger.error(f"Profiles file not found at {PROFILES_PATH}")
        sys.exit(1)

    with open(PROFILES_PATH, "r", encoding="utf-8") as f:
        profiles_data = json.load(f)

    existing_embeddings = {}
    if os.path.exists(OUTPUT_EMBEDDINGS_PATH) and not force_regenerate:
        try:
            with open(OUTPUT_EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
                existing_list = json.load(f)
                for item in existing_list:
                    existing_embeddings[item["image_id"]] = item
            logger.info(f"Loaded {len(existing_embeddings)} existing embeddings from disk.")
        except Exception as e:
            logger.warning(f"Failed to read existing embeddings: {e}")

    has_api_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key")
    model_name = settings.EMBEDDING_MODEL

    output_list = []
    for prof_dict in profiles_data:
        prof = ImageProfile(**prof_dict)
        image_id = prof.image_id
        search_doc = build_search_document(prof)

        # Skip regeneration if valid existing embedding matches search doc and model
        if image_id in existing_embeddings and not force_regenerate:
            existing = existing_embeddings[image_id]
            if existing.get("search_document") == search_doc and existing.get("model_used") == model_name:
                logger.info(f"Reusing existing embedding for {image_id}")
                output_list.append(existing)
                continue

        embedding_vector = None
        embedding_source = "provider"
        if has_api_key:
            try:
                logger.info(f"Generating live embedding for {image_id}...")
                embedding_vector = gemini_client.embed_text(search_doc)
            except Exception as e:
                logger.warning(f"Live embedding API call failed for {image_id}: {e}.")

        if not embedding_vector:
            if not settings.ALLOW_SYNTHETIC_AI:
                raise RuntimeError(
                    f"Live embedding generation failed for {image_id} and ALLOW_SYNTHETIC_AI=false. "
                    f"Production demo embeddings cannot use synthetic vectors."
                )
            logger.info(f"Using synthetic deterministic vector for {image_id}")
            embedding_vector = generate_deterministic_synthetic_vector(search_doc)
            embedding_source = "synthetic"

        record = {
            "image_id": image_id,
            "embedding": embedding_vector,
            "search_document": search_doc,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_used": model_name if embedding_source == "provider" else f"{model_name}-synthetic",
            "embedding_source": embedding_source,
        }
        output_list.append(record)

    with open(OUTPUT_EMBEDDINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(output_list, f, indent=2)

    logger.info(f"Successfully saved {len(output_list)} demo embeddings to {OUTPUT_EMBEDDINGS_PATH}")


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    main(force_regenerate=force_flag)
