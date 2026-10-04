from __future__ import annotations
from typing import List
from app.models.image import ImageProfile


def build_search_document(profile: ImageProfile) -> str:
    """
    Generates a normalized, deterministic text representation of an ImageProfile
    suitable for semantic retrieval & embedding generation.
    Uses strictly observable metadata and manual identity_tags.
    Excludes internal IDs, file paths, model names, AI reasoning, and warnings.
    """
    parts: List[str] = []

    # People
    people_items: List[str] = []
    if profile.people_count:
        people_items.append(f"count: {profile.people_count}")
    if profile.people_age_group:
        people_items.append(", ".join(profile.people_age_group))
    if profile.people_description:
        people_items.append(profile.people_description)
    if people_items:
        parts.append(f"People: {'; '.join(people_items)}.")

    # Setting
    setting_items: List[str] = []
    if profile.setting:
        setting_items.append(profile.setting)
    if profile.setting_type:
        setting_items.append(profile.setting_type)
    if profile.setting_details:
        setting_items.append(profile.setting_details)
    if setting_items:
        parts.append(f"Setting: {', '.join(setting_items)}.")

    # Time & Season
    time_items: List[str] = []
    if profile.time_of_day:
        time_items.append(f"time: {profile.time_of_day}")
    if profile.season_hint:
        time_items.append(f"season: {profile.season_hint}")
    if time_items:
        parts.append(f"Environment: {', '.join(time_items)}.")

    # Activity & Occasion
    if profile.activity:
        parts.append(f"Activity: {profile.activity}.")
    if profile.occasion:
        parts.append(f"Occasion: {profile.occasion}.")

    # Clothing
    if profile.clothing:
        parts.append(f"Clothing: {', '.join(profile.clothing)}.")

    # Objects
    if profile.objects:
        parts.append(f"Objects: {', '.join(profile.objects)}.")

    # Animals
    if profile.animals:
        parts.append(f"Animals: {', '.join(profile.animals)}.")

    # Colors
    if profile.dominant_colors:
        parts.append(f"Colors: {', '.join(profile.dominant_colors)}.")

    # Mood & Composition
    if profile.mood:
        parts.append(f"Mood: {profile.mood}.")
    if profile.composition:
        parts.append(f"Composition: {profile.composition}.")

    # Manual Identity Tags
    if profile.identity_tags:
        parts.append(f"Known identities: {', '.join(profile.identity_tags)}.")

    # Free Description
    if profile.free_description:
        parts.append(f"Description: {profile.free_description}")

    return "\n".join(parts)
