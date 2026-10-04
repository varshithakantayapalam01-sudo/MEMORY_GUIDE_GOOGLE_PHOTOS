from __future__ import annotations
import uuid
import json
import logging
from typing import List, Tuple
from google.genai import types
from app.config import settings
from app.models.question import QuestionSelection, ClarificationQuestion
from app.services import gemini_client

logger = logging.getLogger("memory_guide.question_generator")


def generate_fallback_question_phrasing(selection: QuestionSelection, round_num: int) -> Tuple[str, List[str]]:
    """
    Deterministic fallback phrasing for a selected QuestionSelection.
    The fallback NEVER chooses the discriminator itself; it only phrases the selected one.
    Uses candidate distribution to construct concrete, specific options.
    """
    dim = selection.dimension
    val = selection.value or ""
    subkey = selection.subattribute_key
    dist = selection.distribution or {}

    if selection.selection_type == "categorical":
        if dim == "setting":
            return (
                "Do you remember if the photo was taken indoors or outdoors?",
                ["Indoors", "Outdoors", "I don't remember"],
            )
        elif dim == "setting_type":
            top_vals = [k.title() for k, _ in sorted(dist.items(), key=lambda x: x[1], reverse=True) if k and k != "unclear"][:3]
            if not top_vals and val:
                top_vals = [val.title()]
            if not top_vals:
                top_vals = ["At Home", "At A Restaurant", "Outdoors"]
            
            opts_str = ", ".join(top_vals[:-1]) + f", or {top_vals[-1]}" if len(top_vals) > 1 else top_vals[0]
            return (
                f"Do you remember whether it was {opts_str.lower()}?",
                top_vals + ["I don't remember"],
            )
        elif dim == "people_count":
            return (
                "Do you recall how many people were visible in the photo?",
                ["Solo (1 person)", "2 people", "Group (3+ people)", "I don't remember"],
            )
        elif dim == "occasion":
            top_vals = [k.title() for k, _ in sorted(dist.items(), key=lambda x: x[1], reverse=True) if k and k != "unclear"][:3]
            if not top_vals:
                top_vals = ["Birthday", "Wedding", "Festival"]
            opts_str = ", ".join(top_vals[:-1]) + f", or {top_vals[-1]}" if len(top_vals) > 1 else top_vals[0]
            return (
                f"Was this photo taken during a specific occasion like {opts_str.lower()}?",
                top_vals + ["Casual", "I don't remember"],
            )
        elif dim == "activity":
            top_vals = [k.title() for k, _ in sorted(dist.items(), key=lambda x: x[1], reverse=True) if k and k != "unclear"][:3]
            if not top_vals:
                top_vals = ["Celebrating", "Eating", "Posing"]
            return (
                f"Do you remember what primary activity was taking place ({', '.join(top_vals)})?",
                top_vals + ["I don't remember"],
            )
        elif dim == "time_of_day":
            return (
                "Was this photo taken during the day, sunset, or at night?",
                ["Daytime", "Sunset / Golden hour", "Night", "I don't remember"],
            )
        elif dim == "animals":
            return (
                "Was an animal or pet present in the photo?",
                ["Yes, a pet/dog", "No animals", "I don't remember"],
            )
        elif dim == "mood":
            return (
                "Was the photo candid, posed, or happy?",
                ["Candid", "Posed", "Happy", "I don't remember"],
            )
        elif dim == "season_hint":
            return (
                "What season was the photo taken in?",
                ["Summer", "Winter", "Spring / Fall", "I don't remember"],
            )
        else:
            clean_dim = dim.replace('_', ' ')
            top_vals = [k.title() for k, _ in sorted(dist.items(), key=lambda x: x[1], reverse=True) if k and k != "unclear"][:2]
            if top_vals:
                opts_str = f"{top_vals[0]} or {top_vals[-1]}" if len(top_vals) > 1 else top_vals[0]
                return (
                    f"Was the {clean_dim} {opts_str.lower()}?",
                    top_vals + ["I don't remember"],
                )
            v_title = val.title() if val else clean_dim.title()
            return (
                f"Was the {clean_dim} {v_title.lower()}?",
                [v_title, f"Not {v_title}", "I don't remember"],
            )

    else:
        # List Subattributes (Binary)
        if subkey == "objects:cake" or val == "cake":
            return ("Was a cake visible in the photo?", ["Yes", "No", "I don't remember"])
        elif subkey == "objects:balloons" or val == "balloons":
            return ("Were balloons visible in the photo?", ["Yes", "No", "I don't remember"])
        elif subkey == "objects:frisbee" or val == "frisbee":
            return ("Were you or others playing with a frisbee?", ["Yes", "No", "I don't remember"])
        elif subkey == "objects:dog" or val == "dog":
            return ("Was a dog visible in the photo?", ["Yes", "No", "I don't remember"])
        elif dim == "clothing":
            return (f"Do you remember wearing something {val} in the photo?", ["Yes", "No", "I don't remember"])
        elif dim == "dominant_colors":
            return (f"Was {val} a prominent color in the photo?", ["Yes", "No", "I don't remember"])
        else:
            return (f"Was a {val} present or visible in the photo?", ["Yes", "No", "I don't remember"])


def generate_clarification_question(selection: QuestionSelection, round_num: int) -> ClarificationQuestion:
    """
    Generates a ClarificationQuestion object.
    Uses Gemini LLM for natural phrasing when available; otherwise uses fallback templates.
    """
    question_id = f"q_{round_num}_{uuid.uuid4().hex[:8]}"

    has_api_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key")
    text = None
    options = None

    if has_api_key:
        try:
            client = gemini_client._get_client()
            prompt = f"""
You are a memory guide agent phrasing a single clarification question.
The discrimination engine has ALREADY chosen what attribute to ask:
Dimension: {selection.dimension}
Subattribute: {selection.subattribute_key or 'N/A'}
Value/Focus: {selection.value or 'N/A'}
Selection Type: {selection.selection_type}

Rules:
1. Phrase one concise, neutral, non-leading clarification question.
2. Provide 2-4 clear answer choices. Always include "I don't remember" as the final choice.
3. Do NOT create leading memory (e.g. use "Do you remember..." or "Was a... visible?").
4. Return ONLY JSON:
{{
  "text": "Do you remember if the photo was taken indoors or outdoors?",
  "options": ["Indoors", "Outdoors", "I don't remember"]
}}
"""
            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            )
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[prompt],
                config=config,
            )
            if response and response.text:
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                parsed = json.loads(raw_text.strip())
                text = parsed.get("text")
                options = parsed.get("options")
        except Exception as e:
            logger.warning(f"Gemini question phrasing failed ({e}). Using fallback generator.")

    if not text or not options:
        text, options = generate_fallback_question_phrasing(selection, round_num)

    return ClarificationQuestion(
        question_id=question_id,
        round=round_num,
        text=text,
        dimension_tested=selection.dimension,
        subattribute_key=selection.subattribute_key,
        options=options,
        selection_metadata=selection,
    )
