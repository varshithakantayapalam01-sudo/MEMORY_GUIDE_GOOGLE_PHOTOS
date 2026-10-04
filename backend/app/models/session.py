from datetime import datetime, timezone
from typing import Literal, Optional, List, Set
from pydantic import BaseModel, Field
from app.models.clue import Clue
from app.models.candidate import CandidateEntry
from app.models.question import ClarificationQuestion


SessionMode = Literal["demo", "research"]
RetrievalStatus = Literal[
    "created",
    "indexing",
    "ready",
    "in_progress",
    "showing_candidates",
    "found",
    "unresolved",
    "abandoned",
]


class QuestionAnswerRecord(BaseModel):
    question_id: str
    round: int

    dimension: str
    subattribute_key: Optional[str] = None

    question_text: str
    answer_text: Optional[str] = None

    parsed_value: Optional[str] = None
    answer_certainty: Optional[str] = None

    was_idk: bool = False

    candidates_before: int
    candidates_after: int

    discrimination_score: Optional[float] = None
    final_question_score: Optional[float] = None

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CandidateHistoryEntry(BaseModel):
    round: int
    trigger: str

    active_count: int
    reserve_count: int
    rejected_count: int

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RetrievalSession(BaseModel):
    session_id: str
    mode: SessionMode
    retrieval_status: RetrievalStatus = "created"

    original_query: str = ""
    clues: List[Clue] = Field(default_factory=list)

    # Coverage Tracking
    dimensions_asked: Set[str] = Field(default_factory=set)
    subattributes_asked: Set[str] = Field(default_factory=set)
    dimensions_provided_by_user: Set[str] = Field(default_factory=set)
    consecutive_idk_count: int = 0
    total_idk_count: int = 0

    # Candidate State
    active_candidates: List[CandidateEntry] = Field(default_factory=list)
    reserve_candidates: List[CandidateEntry] = Field(default_factory=list)
    explicitly_rejected_ids: Set[str] = Field(default_factory=set)

    # Question State
    current_question: Optional[ClarificationQuestion] = None
    question_history: List[QuestionAnswerRecord] = Field(default_factory=list)

    # Retrieval History
    candidate_history: List[CandidateHistoryEntry] = Field(default_factory=list)
    round_count: int = 0

    # Outcome
    final_target_id: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None
