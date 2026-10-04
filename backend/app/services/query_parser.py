from __future__ import annotations
import json
import re
import logging
from typing import List, Dict, Any
from app.config import settings
from app.models.clue import Clue, ClueCertainty
from app.services import gemini_client

logger = logging.getLogger("memory_guide.query_parser")

QUERY_PARSER_PROMPT = """
You are a precise query understanding agent for a vague photo retrieval system.
Analyze the user's vague photo description and extract structured clues.

Rules:
1. Extract clues for observable dimensions: setting (indoor/outdoor), setting_type, activity, occasion, clothing, objects, dominant_colors, people_count, people_age_group, animals, mood, time_of_day, season_hint.
2. Determine certainty level strictly from phrasing:
   - "definite": explicit statements ("I was wearing pink", "there was a cake")
   - "probable": hedge phrases ("I think I was wearing pink", "probably outdoors")
   - "unsure": weak/doubtful phrases ("maybe a cake", "possibly at night")
   - "inferred": implicit context inferred from other clues
3. For list dimensions (clothing, objects, dominant_colors), set subattribute_key as "<dimension>:<value_slug>".
4. Do NOT hallucinate or assume identities unless explicitly stated as personal names or relations.

Return ONLY a JSON list of clue objects:
[
  {
    "dimension": "clothing",
    "value": "pink dress",
    "source": "user_initial",
    "certainty": "probable",
    "subattribute_key": "clothing:pink_dress",
    "raw_text": "I think I was wearing a pink dress"
  }
]
"""


def detect_certainty_from_phrase(phrase: str) -> ClueCertainty:
    """Helper to detect certainty level from linguistic hedges."""
    lower = phrase.lower()
    if any(kw in lower for kw in ["maybe", "might", "possibly", "could be", "not sure", "guess"]):
        return "unsure"
    elif any(kw in lower for kw in ["think", "probably", "believe", "pretty sure", "recollect"]):
        return "probable"
    else:
        return "definite"


def parse_query_fallback(raw_query: str) -> List[Clue]:
    """
    Deterministic rule-based fallback query parser when Gemini API is unavailable.
    Detects key memory dimensions and certainty levels.
    """
    clues: List[Clue] = []
    text = raw_query.strip()
    if not text:
        return clues

    certainty = detect_certainty_from_phrase(text)
    lower = text.lower()

    # Setting: indoor / outdoor
    if "indoor" in lower or "inside" in lower or "living room" in lower or "home" in lower:
        clues.append(Clue(
            dimension="setting",
            value="indoor",
            source="user_initial",
            certainty=certainty,
            raw_text=text
        ))
    elif "outdoor" in lower or "outside" in lower or "park" in lower or "beach" in lower or "garden" in lower:
        clues.append(Clue(
            dimension="setting",
            value="outdoor",
            source="user_initial",
            certainty=certainty,
            raw_text=text
        ))

    # Occasion / Activity
    if "birthday" in lower or "bday" in lower:
        clues.append(Clue(
            dimension="occasion",
            value="birthday",
            source="user_initial",
            certainty=certainty,
            raw_text=text
        ))
    elif "wedding" in lower:
        clues.append(Clue(
            dimension="occasion",
            value="wedding",
            source="user_initial",
            certainty=certainty,
            raw_text=text
        ))
    elif "picnic" in lower:
        clues.append(Clue(
            dimension="occasion",
            value="picnic",
            source="user_initial",
            certainty=certainty,
            raw_text=text
        ))
    elif "festival" in lower or "diwali" in lower:
        clues.append(Clue(
            dimension="occasion",
            value="festival",
            source="user_initial",
            certainty=certainty,
            raw_text=text
        ))

    # Objects: cake, balloons, frisbee, beach/waves, sweets
    if "cake" in lower:
        clues.append(Clue(
            dimension="objects",
            value="cake",
            source="user_initial",
            certainty=certainty,
            subattribute_key="objects:cake",
            raw_text=text
        ))
    if "balloon" in lower:
        clues.append(Clue(
            dimension="objects",
            value="balloons",
            source="user_initial",
            certainty=certainty,
            subattribute_key="objects:balloons",
            raw_text=text
        ))
    if "frisbee" in lower:
        clues.append(Clue(
            dimension="objects",
            value="frisbee",
            source="user_initial",
            certainty=certainty,
            subattribute_key="objects:frisbee",
            raw_text=text
        ))

    # Clothing / Colors
    color_keywords = ["pink", "yellow", "blue", "red", "green", "white", "black", "gold"]
    for col in color_keywords:
        if col in lower:
            clues.append(Clue(
                dimension="dominant_colors",
                value=col,
                source="user_initial",
                certainty=certainty,
                subattribute_key=f"dominant_colors:{col}",
                raw_text=text
            ))
            if "wear" in lower or "shirt" in lower or "dress" in lower or "sweater" in lower or "jacket" in lower:
                clues.append(Clue(
                    dimension="clothing",
                    value=f"{col} clothing",
                    source="user_initial",
                    certainty=certainty,
                    subattribute_key=f"clothing:{col}",
                    raw_text=text
                ))

    return clues


def parse_query_to_clues(raw_query: str) -> List[Clue]:
    """
    Parses a raw vague user description into a structured list of Clues.
    Uses Gemini LLM when available, with fallback to rule-based parser.
    """
    if not raw_query or not raw_query.strip():
        return []

    has_api_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key")
    if not has_api_key:
        return parse_query_fallback(raw_query)

    try:
        client = gemini_client._get_client()
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[raw_query, QUERY_PARSER_PROMPT],
            config={"temperature": 0.1, "response_mime_type": "application/json"},
        )

        if not response or not response.text:
            return parse_query_fallback(raw_query)

        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        parsed = json.loads(raw_text.strip())
        if not isinstance(parsed, list):
            return parse_query_fallback(raw_query)

        clues = []
        for item in parsed:
            dim = item.get("dimension")
            val = item.get("value")
            cert = item.get("certainty", "probable")
            if cert not in ("definite", "probable", "unsure", "inferred"):
                cert = "probable"
            sub_key = item.get("subattribute_key")
            if not sub_key and dim in ("clothing", "objects", "dominant_colors"):
                sub_key = f"{dim}:{val}"

            if dim and val:
                clues.append(Clue(
                    dimension=str(dim),
                    value=str(val),
                    source="user_initial",
                    certainty=cert,
                    subattribute_key=sub_key,
                    raw_text=item.get("raw_text", raw_query),
                ))
        return clues if clues else parse_query_fallback(raw_query)

    except Exception as e:
        logger.warning(f"Gemini query parsing failed ({e}). Using fallback parser.")
        return parse_query_fallback(raw_query)
