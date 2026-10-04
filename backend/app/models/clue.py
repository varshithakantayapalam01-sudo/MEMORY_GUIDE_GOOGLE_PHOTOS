from typing import Literal, Optional, Dict
from pydantic import BaseModel


ClueSource = Literal["user_initial", "user_answer", "inferred"]
ClueCertainty = Literal["definite", "probable", "unsure", "inferred"]
CluePolarity = Literal["positive", "negative"]

CERTAINTY_WEIGHTS: Dict[ClueCertainty, float] = {
    "definite": 1.00,
    "probable": 0.70,
    "unsure": 0.40,
    "inferred": 0.20,
}


class Clue(BaseModel):
    dimension: str
    value: str
    source: ClueSource
    certainty: ClueCertainty
    polarity: CluePolarity = "positive"
    subattribute_key: Optional[str] = None
    raw_text: Optional[str] = None
