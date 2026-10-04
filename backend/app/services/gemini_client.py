from __future__ import annotations
import json
import time
import logging
from typing import Any, Dict
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger("memory_guide.gemini_client")


class GeminiAPIError(Exception):
    """Exception raised when Gemini API call fails."""

    pass


class GeminiParseError(Exception):
    """Exception raised when Gemini output cannot be parsed into structured JSON."""

    pass


# Prompt template requesting structured visual attribute extraction
VLM_EXTRACTION_PROMPT = """
Analyze this photo and extract ONLY observable visual attributes. Do NOT hallucinate names, personal relationships, exact dates, exact locations, or backstories.

Extract the following JSON structure:
{
  "people_count": "0, 1, 2, or 3+",
  "people_age_group": ["child", "teen", "adult", "elderly"],
  "people_description": "short factual description of visible people",
  "setting": "indoor or outdoor",
  "setting_type": "e.g. home, park, beach, restaurant, office, street",
  "setting_details": "short factual description of environment",
  "time_of_day": "day, night, golden_hour, or unclear",
  "season_hint": "summer, winter, rainy, or unclear",
  "activity": "primary activity e.g. celebrating, eating, playing, posing, traveling",
  "occasion": "event if clearly visible e.g. birthday, wedding, festival, casual",
  "clothing": ["list of clothing descriptions for visible people"],
  "objects": ["list of prominent objects visible"],
  "animals": ["list of animals present e.g. dog, cat, or empty"],
  "dominant_colors": ["list of top 2-3 dominant colors"],
  "mood": "happy, serious, candid, or posed",
  "composition": "selfie, posed, candid, or group",
  "free_description": "a 1-2 sentence factual summary of the image"
}

If any attribute is unclear or not present, use "unclear", null, or [].
Do NOT include any identity names (such as "sister", "Rahul", "mom").
"""


def _get_client() -> genai.Client:
    """Initializes and returns a Google GenAI client using settings."""
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key":
        raise GeminiAPIError("GEMINI_API_KEY is not configured in backend environment.")
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def analyze_image(image_bytes: bytes, mime_type: str = "image/jpeg", max_retries: int = 1) -> Dict[str, Any]:
    """
    Analyzes raw image bytes using Gemini Vision and returns structured attribute profile dictionary.
    NEVER logs raw image bytes or API keys.
    """
    if not image_bytes:
        raise GeminiAPIError("Cannot analyze empty image bytes.")

    model_name = settings.GEMINI_MODEL
    logger.info(f"Initiating Gemini vision analysis using model '{model_name}' (size: {len(image_bytes)} bytes)")

    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            client = _get_client()
            
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type or "image/jpeg"
            )

            config = types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            )

            response = client.models.generate_content(
                model=model_name,
                contents=[image_part, VLM_EXTRACTION_PROMPT],
                config=config,
            )

            if not response or not response.text:
                raise GeminiAPIError("Gemini API returned an empty response.")

            raw_text = response.text.strip()
            
            # Clean potential markdown code blocks
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

            try:
                parsed_json = json.loads(raw_text)
                if not isinstance(parsed_json, dict):
                    raise GeminiParseError("Parsed output is not a JSON object.")
                logger.info("Gemini vision analysis completed successfully.")
                return parsed_json
            except json.JSONDecodeError as e:
                raise GeminiParseError(f"Failed to parse Gemini output as JSON: {e}")

        except (GeminiAPIError, GeminiParseError) as e:
            last_exception = e
            logger.warning(f"Gemini API attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(0.5)
        except Exception as e:
            last_exception = GeminiAPIError(f"Unexpected Gemini API error: {e}")
            logger.warning(f"Gemini API unexpected error on attempt {attempt}: {e}")
            if attempt < max_retries:
                time.sleep(0.5)

    raise last_exception or GeminiAPIError("Gemini vision analysis failed after retries.")


def embed_text(text: str, max_retries: int = 1) -> list[float]:
    """
    Generates a dense vector embedding for input text using settings.EMBEDDING_MODEL.
    Validates input and output, handles transient errors with retries, and NEVER logs API keys.
    """
    if not text or not text.strip():
        raise GeminiAPIError("Cannot embed empty or whitespace-only text.")

    model_name = settings.EMBEDDING_MODEL
    logger.info(f"Generating text embedding using model '{model_name}' (text length: {len(text)})")

    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            client = _get_client()
            response = client.models.embed_content(
                model=model_name,
                contents=text.strip(),
            )

            if not response:
                raise GeminiAPIError("Gemini embedding API returned empty response.")

            # Extract embedding vector values
            embedding_vals = None
            if hasattr(response, "embedding") and response.embedding and hasattr(response.embedding, "values"):
                embedding_vals = response.embedding.values
            elif hasattr(response, "embeddings") and response.embeddings and len(response.embeddings) > 0:
                embedding_vals = response.embeddings[0].values

            if not embedding_vals or not isinstance(embedding_vals, (list, tuple)):
                raise GeminiAPIError("Failed to extract embedding vector values from Gemini API response.")

            vector = [float(v) for v in embedding_vals]
            if len(vector) == 0:
                raise GeminiAPIError("Gemini embedding vector is empty.")

            logger.info(f"Embedding generated successfully (dim: {len(vector)})")
            return vector

        except GeminiAPIError as e:
            last_exception = e
            logger.warning(f"Gemini embedding API attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(0.5)
        except Exception as e:
            last_exception = GeminiAPIError(f"Unexpected Gemini embedding error: {e}")
            logger.warning(f"Gemini embedding unexpected error on attempt {attempt}: {e}")
            if attempt < max_retries:
                time.sleep(0.5)

    raise last_exception or GeminiAPIError("Gemini embedding generation failed after retries.")

