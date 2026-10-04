from typing import Any, Optional, Dict
from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    mode: str


class QueryRequest(BaseModel):
    query: str


class AnswerRequest(BaseModel):
    answerText: str
    questionId: Optional[str] = None


class SelectRequest(BaseModel):
    selectionType: str  # "found", "none", "close"
    imageId: Optional[str] = None
    rejectedImageIds: Optional[list[str]] = None



class SessionSummaryResponseData(BaseModel):
    sessionId: str
    mode: str
    status: str
    startedAt: str
    cluesCount: int = 0
    activeCandidateCount: int = 0
    reserveCandidateCount: int = 0
    rejectedCandidateCount: int = 0
    roundCount: int = 0
    consecutiveIdkCount: int = 0
    totalIdkCount: int = 0


class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, str]] = None
