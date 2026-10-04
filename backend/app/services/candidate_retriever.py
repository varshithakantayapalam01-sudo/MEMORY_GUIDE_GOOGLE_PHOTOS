from __future__ import annotations
import math
import logging
from typing import List, Dict, Any, Tuple
from app.models.clue import Clue, CERTAINTY_WEIGHTS
from app.models.candidate import CandidateEntry
from app.models.image import ImageProfile

logger = logging.getLogger("memory_guide.candidate_retriever")


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Computes deterministic cosine similarity between two float vectors.
    Returns float in [-1.0, 1.0]. Returns 0.0 if either vector is zero norm.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    sim = dot_product / (norm_a * norm_b)
    # Clamp for numerical stability
    return max(-1.0, min(1.0, sim))


def normalize_cosine_score(raw_sim: float) -> float:
    """
    Normalizes cosine similarity from [-1, 1] to [0, 1] interval.
    """
    return max(0.0, min(1.0, (raw_sim + 1.0) / 2.0))


def compute_structured_clue_agreement(profile: ImageProfile, clues: List[Clue]) -> float:
    """
    Computes a deterministic structured clue agreement score in [0.0, 1.0].
    Applies CERTAINTY_WEIGHTS: definite=1.0, probable=0.7, unsure=0.4, inferred=0.2.
    """
    if not clues:
        return 0.5  # Neutral default score when no clues provided

    accumulated_delta = 0.0
    for clue in clues:
        weight = CERTAINTY_WEIGHTS.get(clue.certainty, 0.7)

        dim = clue.dimension
        val = clue.value.lower()

        matched = False
        contradicted = False

        # Match check against profile
        if dim == "setting":
            if profile.setting and profile.setting.lower() == val:
                matched = True
            elif profile.setting and profile.setting.lower() not in ("unclear", val):
                contradicted = True

        elif dim == "occasion":
            if profile.occasion and val in profile.occasion.lower():
                matched = True

        elif dim == "activity":
            if profile.activity and val in profile.activity.lower():
                matched = True

        elif dim in ("clothing", "objects", "dominant_colors", "animals"):
            prof_list = getattr(profile, dim, [])
            if any(val in str(item).lower() or str(item).lower() in val for item in prof_list):
                matched = True

        elif dim == "people_count":
            if profile.people_count and profile.people_count == val:
                matched = True

        elif dim == "identity":
            if any(val in tag.lower() for tag in profile.identity_tags):
                matched = True

        # Fallback check free_description
        if not matched and not contradicted and profile.free_description:
            if val in profile.free_description.lower():
                matched = True

        # Handle negative polarity clues
        if clue.polarity == "negative":
            # For negative clue (e.g. no cake), if profile contains the item, it's contradicted.
            # If profile does NOT contain the item, it matches.
            has_item = matched
            matched = not has_item and not contradicted
            contradicted = has_item

        if matched:
            accumulated_delta += 0.5 * weight
        elif contradicted:
            accumulated_delta += -0.25 * weight

    base_score = 0.5 + (accumulated_delta / len(clues))
    return max(0.0, min(1.0, base_score))



def rank_candidates_composite(
    query_embedding: List[float],
    image_embeddings: Dict[str, List[float]],
    image_profiles: Dict[str, ImageProfile],
    clues: List[Clue],
    weight_semantic: float = 0.80,
    weight_structured: float = 0.20,
) -> List[Tuple[str, float, float, float]]:
    """
    Ranks candidate images using the inspectable composite formula:
    final_score = 0.80 * semantic_score + 0.20 * structured_score

    Returns list of tuples: (image_id, final_score, semantic_score, structured_score) sorted descending by final_score.
    """
    results: List[Tuple[str, float, float, float]] = []

    for image_id, img_emb in image_embeddings.items():
        prof = image_profiles.get(image_id)
        if not prof:
            continue

        raw_sim = cosine_similarity(query_embedding, img_emb)
        sem_score = normalize_cosine_score(raw_sim)

        struct_score = compute_structured_clue_agreement(prof, clues)

        final_score = (weight_semantic * sem_score) + (weight_structured * struct_score)
        results.append((image_id, final_score, sem_score, struct_score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results
