from typing import Literal, Optional, List
from pydantic import BaseModel, Field
from app.models.image import ImageProfile


CandidatePool = Literal["active", "reserve", "rejected"]


class CandidateEntry(BaseModel):
    image_id: str
    score: float
    semantic_score: Optional[float] = None
    structured_score: Optional[float] = None
    rank: Optional[int] = None
    profile: Optional[ImageProfile] = None
    pool: CandidatePool
    match_reasons: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)

