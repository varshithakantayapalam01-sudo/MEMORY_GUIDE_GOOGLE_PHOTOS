from typing import Literal, Optional, List, Dict
from pydantic import BaseModel, Field


QuestionSelectionType = Literal["categorical", "subattribute"]


class QuestionSelection(BaseModel):
    selection_type: QuestionSelectionType
    dimension: str
    subattribute_key: Optional[str] = None
    value: Optional[str] = None

    discrimination_score: float
    memorability_weight: float
    final_score: float

    distribution: Dict[str, float] = Field(default_factory=dict)


class ClarificationQuestion(BaseModel):
    question_id: str
    round: int
    text: str

    dimension_tested: str
    subattribute_key: Optional[str] = None

    options: List[str] = Field(default_factory=list)

    selection_metadata: Optional[QuestionSelection] = None
