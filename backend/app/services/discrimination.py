from __future__ import annotations
import logging
from typing import Dict, List, Optional, Set, Tuple
from app.models.session import RetrievalSession
from app.models.question import QuestionSelection
from app.models.image import ImageProfile
from app.services import image_understanding_service

logger = logging.getLogger("memory_guide.discrimination")

# Memorability weights per dimension
MEMORABILITY_WEIGHTS: Dict[str, float] = {
    "people_count": 1.0,
    "setting": 1.0,
    "people_age_group": 0.9,
    "occasion": 0.9,
    "activity": 0.9,
    "setting_type": 0.8,
    "animals": 0.8,
    "clothing": 0.7,
    "objects": 0.7,
    "time_of_day": 0.6,
    "season_hint": 0.5,
    "mood": 0.4,
    "dominant_colors": 0.3,
}

CATEGORICAL_DIMENSIONS: List[str] = [
    "setting",
    "setting_type",
    "people_count",
    "people_age_group",
    "occasion",
    "activity",
    "time_of_day",
    "animals",
]

LIST_DIMENSIONS: List[str] = [
    "objects",
    "clothing",
    "dominant_colors",
]

MIN_QUESTION_VALUE = 0.10


def get_excluded_keys(session: RetrievalSession) -> Tuple[Set[str], Set[str]]:
    """
    Returns sets of excluded dimensions and excluded subattribute_keys.
    """
    excluded_dims: Set[str] = set()
    excluded_subkeys: Set[str] = set()

    # From session tracking
    excluded_dims.update(session.dimensions_asked)
    excluded_dims.update(session.dimensions_provided_by_user)
    excluded_subkeys.update(session.subattributes_asked)

    # From session clues (initial or answered)
    for clue in session.clues:
        excluded_dims.add(clue.dimension)
        if clue.subattribute_key:
            excluded_subkeys.add(clue.subattribute_key)
        if clue.dimension in LIST_DIMENSIONS and clue.value:
            excluded_subkeys.add(f"{clue.dimension}:{clue.value.lower().strip()}")

    return excluded_dims, excluded_subkeys


def select_next_best_question(session: RetrievalSession) -> Optional[QuestionSelection]:
    """
    Calculates the single most useful missing clue among CURRENT active candidates.
    Uses relevance-weighted distributions and memorability weights.
    Returns QuestionSelection if final_score >= MIN_QUESTION_VALUE (0.10), else None.
    """
    active_entries = session.active_candidates
    if not active_entries:
        logger.info("No active candidates to discriminate.")
        return None

    # Load ImageProfiles for active candidates
    profiles_list = image_understanding_service.get_session_profiles(session.session_id)
    profiles_map = {p.image_id: p for p in profiles_list}

    for e in active_entries:
        if e.image_id not in profiles_map and e.profile:
            if isinstance(e.profile, ImageProfile):
                profiles_map[e.image_id] = e.profile
            elif isinstance(e.profile, dict):
                try:
                    profiles_map[e.image_id] = ImageProfile(**e.profile)
                except Exception:
                    pass

    valid_entries = [e for e in active_entries if e.image_id in profiles_map]
    if not valid_entries:
        return None

    # 1. Relevance weights: w_i = score_i / sum(scores)
    total_score = sum(max(0.0001, e.score) for e in valid_entries)
    weights: Dict[str, float] = {
        e.image_id: max(0.0001, e.score) / total_score for e in valid_entries
    }

    excluded_dims, excluded_subkeys = get_excluded_keys(session)

    candidates_selections: List[QuestionSelection] = []

    # 2. Evaluate Categorical Dimensions
    for dim in CATEGORICAL_DIMENSIONS:
        if dim in excluded_dims:
            continue

        weighted_counts: Dict[str, float] = {}
        for entry in valid_entries:
            prof = profiles_map[entry.image_id]
            val = getattr(prof, dim, None)

            if isinstance(val, list):
                # e.g., people_age_group
                for item in val:
                    val_str = str(item).lower().strip()
                    if val_str and val_str != "unclear":
                        weighted_counts[val_str] = weighted_counts.get(val_str, 0.0) + weights[entry.image_id]
            elif val:
                val_str = str(val).lower().strip()
                if val_str and val_str != "unclear":
                    weighted_counts[val_str] = weighted_counts.get(val_str, 0.0) + weights[entry.image_id]

        if not weighted_counts or len(weighted_counts) <= 1:
            continue

        sum_dist = sum(weighted_counts.values())
        if sum_dist <= 0:
            continue
        dist = {k: v / sum_dist for k, v in weighted_counts.items()}

        max_frac = max(dist.values())
        disc_score = 1.0 - max_frac
        mem_weight = MEMORABILITY_WEIGHTS.get(dim, 0.5)
        final_score = disc_score * mem_weight

        top_val = max(dist, key=dist.get)

        candidates_selections.append(QuestionSelection(
            selection_type="categorical",
            dimension=dim,
            subattribute_key=None,
            value=top_val,
            discrimination_score=round(disc_score, 4),
            memorability_weight=mem_weight,
            final_score=round(final_score, 4),
            distribution={k: round(v, 4) for k, v in dist.items()},
        ))

    # 3. Evaluate List Dimensions & Subattributes
    for dim in LIST_DIMENSIONS:
        if dim in excluded_dims:
            continue

        subattribute_weights: Dict[str, float] = {}
        for entry in valid_entries:
            prof = profiles_map[entry.image_id]
            items = getattr(prof, dim, []) or []
            for item in items:
                v_slug = str(item).lower().strip()
                if v_slug and v_slug != "unclear":
                    subattribute_weights[v_slug] = subattribute_weights.get(v_slug, 0.0) + weights[entry.image_id]

        for v_slug, p in subattribute_weights.items():
            subkey = f"{dim}:{v_slug}"
            if subkey in excluded_subkeys:
                continue

            # split_score = 1 - abs(2*p - 1)
            # p near 0.5 gives split_score near 1.0
            split_score = 1.0 - abs(2.0 * p - 1.0)
            mem_weight = MEMORABILITY_WEIGHTS.get(dim, 0.5)
            final_score = split_score * mem_weight

            candidates_selections.append(QuestionSelection(
                selection_type="subattribute",
                dimension=dim,
                subattribute_key=subkey,
                value=v_slug,
                discrimination_score=round(split_score, 4),
                memorability_weight=mem_weight,
                final_score=round(final_score, 4),
                distribution={"present": round(p, 4), "absent": round(1.0 - p, 4)},
            ))

    if not candidates_selections:
        return None

    # Sort descending by final_score
    candidates_selections.sort(key=lambda s: s.final_score, reverse=True)
    best = candidates_selections[0]

    if best.final_score < MIN_QUESTION_VALUE:
        logger.info(f"Best question candidate score {best.final_score} below MIN_QUESTION_VALUE {MIN_QUESTION_VALUE}")
        return None

    logger.info(
        f"Selected question discriminator: dim='{best.dimension}', subkey='{best.subattribute_key}', "
        f"val='{best.value}', score={best.final_score} (disc: {best.discrimination_score}, mem: {best.memorability_weight})"
    )
    return best
