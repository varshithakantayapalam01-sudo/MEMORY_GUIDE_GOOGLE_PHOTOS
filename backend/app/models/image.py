from typing import Optional, List
from pydantic import BaseModel, Field


class ImageProfile(BaseModel):
    image_id: str
    image_url: Optional[str] = None
    file_path: Optional[str] = None

    people_count: Optional[str] = None
    people_age_group: List[str] = Field(default_factory=list)
    people_description: Optional[str] = None

    setting: Optional[str] = None
    setting_type: Optional[str] = None
    setting_details: Optional[str] = None

    time_of_day: Optional[str] = None
    season_hint: Optional[str] = None

    activity: Optional[str] = None
    occasion: Optional[str] = None

    clothing: List[str] = Field(default_factory=list)
    objects: List[str] = Field(default_factory=list)
    animals: List[str] = Field(default_factory=list)
    dominant_colors: List[str] = Field(default_factory=list)

    mood: Optional[str] = None
    composition: Optional[str] = None

    free_description: Optional[str] = None

    # Manually pre-tagged identity metadata ONLY. Does not imply face recognition.
    identity_tags: List[str] = Field(default_factory=list)

    # Profile validation metadata
    profile_status: str = "complete"  # "complete", "partial", "failed"
    profile_warnings: List[str] = Field(default_factory=list)
