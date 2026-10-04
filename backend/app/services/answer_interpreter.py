from __future__ import annotations
import logging
from typing import Optional, Tuple
from app.models.clue import Clue, ClueCertainty, CluePolarity
from app.models.question import ClarificationQuestion
from app.services import query_parser

logger = logging.getLogger("memory_guide.answer_interpreter")

IDK_KEYWORDS = [
    "don't remember", "dont remember", "idk", "not sure",
    "don't recall", "dont recall", "no idea", "can't remember",
    "cant remember", "unclear", "do not remember", "pass"
]


def is_idk_response(answer_text: str) -> bool:
    """
    Checks if answer text indicates 'I don't remember' / IDK.
    """
    if not answer_text or not answer_text.strip():
        return True
    lower = answer_text.strip().lower()
    return any(kw in lower for kw in IDK_KEYWORDS) or lower in ("i don't remember", "i dont remember", "idk")


def detect_certainty_and_polarity(answer_text: str) -> Tuple[ClueCertainty, CluePolarity]:
    """
    Detects certainty ('definite', 'probable', 'unsure') and polarity ('positive', 'negative')
    from linguistic markers in user answer.
    """
    lower = answer_text.lower().strip()

    # Detect polarity
    is_negative = False
    if lower in ("no", "nope", "not at all", "definitely not", "false", "no cake", "no balloons", "not indoors", "not outdoors"):
        is_negative = True
    elif any(kw in lower for kw in ["no ", "not ", "n't ", "never"]):
        # Check if negative marker present
        is_negative = True

    polarity: CluePolarity = "negative" if is_negative else "positive"

    # Detect certainty
    certainty = query_parser.detect_certainty_from_phrase(lower)
    return certainty, polarity


def interpret_user_answer(
    question: ClarificationQuestion,
    answer_text: str,
) -> Tuple[bool, Optional[Clue]]:
    """
    Interprets user answer text for a ClarificationQuestion.
    Returns Tuple[is_idk, Optional[Clue]].
    If user said 'I don't remember', returns (True, None).
    """
    if is_idk_response(answer_text):
        logger.info(f"User answered IDK to question '{question.question_id}'")
        return True, None

    dim = question.dimension_tested
    subkey = question.subattribute_key
    lower_ans = answer_text.strip().lower()

    certainty, polarity = detect_certainty_and_polarity(answer_text)

    # Subattribute question (e.g. objects:cake or clothing:pink)
    if subkey or ":" in dim:
        if not subkey and ":" in dim:
            subkey = dim
            dim = dim.split(":")[0]

        val_name = subkey.split(":")[1] if subkey and ":" in subkey else question.selection_metadata.value if question.selection_metadata else "item"

        clue = Clue(
            dimension=dim,
            value=val_name,
            source="user_answer",
            certainty=certainty,
            polarity=polarity,
            subattribute_key=subkey,
            raw_text=answer_text,
        )
        return False, clue

    # Categorical question (e.g. setting -> indoor/outdoor)
    if dim == "setting":
        val = "indoor" if ("indoor" in lower_ans or "inside" in lower_ans or "in " in lower_ans) else "outdoor" if ("outdoor" in lower_ans or "outside" in lower_ans or "out" in lower_ans) else "indoor"
        clue = Clue(
            dimension="setting",
            value=val,
            source="user_answer",
            certainty=certainty,
            polarity=polarity,
            raw_text=answer_text,
        )
        return False, clue

    elif dim == "people_count":
        val = "1" if ("1" in lower_ans or "solo" in lower_ans or "alone" in lower_ans) else "2" if ("2" in lower_ans or "couple" in lower_ans or "two" in lower_ans) else "3+"
        clue = Clue(
            dimension="people_count",
            value=val,
            source="user_answer",
            certainty=certainty,
            polarity=polarity,
            raw_text=answer_text,
        )
        return False, clue

    elif dim in ("occasion", "activity", "setting_type", "animals", "time_of_day", "season_hint", "mood"):
        # Match option substring if present in answer
        val = lower_ans
        for opt in question.options:
            opt_clean = opt.lower().replace(" (1 person)", "").replace(" (3+ people)", "")
            if opt_clean in lower_ans and "remember" not in opt_clean:
                val = opt_clean
                break

        clue = Clue(
            dimension=dim,
            value=val,
            source="user_answer",
            certainty=certainty,
            polarity=polarity,
            raw_text=answer_text,
        )
        return False, clue

    # Generic fallback clue
    clue = Clue(
        dimension=dim,
        value=lower_ans,
        source="user_answer",
        certainty=certainty,
        polarity=polarity,
        raw_text=answer_text,
    )
    return False, clue
