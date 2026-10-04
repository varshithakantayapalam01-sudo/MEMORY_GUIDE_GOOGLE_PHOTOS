from __future__ import annotations
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.services import gemini_client, query_parser
from app.models.clue import Clue


def run_query_parser_smoke_test():
    query = "I think this was indoors and I was wearing something pink near a cake."
    has_api_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key")

    provider_used = "Gemini LLM"
    model_used = settings.GEMINI_MODEL
    fallback_used = False
    clues = []
    error_msg = None

    if has_api_key:
        try:
            client = gemini_client._get_client()
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[query, query_parser.QUERY_PARSER_PROMPT],
                config={"temperature": 0.1, "response_mime_type": "application/json"},
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
                for item in parsed:
                    dim = item.get("dimension")
                    val = item.get("value")
                    cert = item.get("certainty", "probable")
                    if dim and val:
                        clues.append(Clue(dimension=str(dim), value=str(val), certainty=cert, source="user_initial", raw_text=query))
            else:
                error_msg = "Gemini returned empty response"
        except Exception as e:
            error_msg = str(e)
    else:
        error_msg = "GEMINI_API_KEY is not configured in backend environment."

    if error_msg:
        if settings.ALLOW_SYNTHETIC_AI:
            clues = query_parser.parse_query_fallback(query)
            fallback_used = True
            provider_used = "rule_based_fallback"
        else:
            fallback_used = False

    print("=== LIVE QUERY PARSER SMOKE TEST RESULTS ===")
    print(f"Input Query: \"{query}\"")
    print(f"Provider Used: {provider_used}")
    print(f"Model Used: {model_used}")
    print(f"Fallback Used: {fallback_used}")

    if error_msg and not fallback_used:
        print(f"Provider Error: {error_msg}")

    print("\nExtracted Structured Clues:")
    for c in clues:
        print(f"  - Dimension: {c.dimension:<15} | Value: {c.value:<15} | Certainty: {c.certainty}")

    # Check key extractions
    setting_found = any(c.dimension == "setting" and "indoor" in c.value.lower() and c.certainty == "probable" for c in clues)
    clothing_found = any(("clothing" in c.dimension or "colors" in c.dimension) and "pink" in c.value.lower() for c in clues)
    object_found = any(c.dimension == "objects" and "cake" in c.value.lower() for c in clues)

    print("\nExtraction Verification:")
    print(f"  - Setting (indoor -> probable): {'VERIFIED' if setting_found else 'NOT VERIFIED'}")
    print(f"  - Clothing (pink -> probable): {'VERIFIED' if clothing_found else 'NOT VERIFIED'}")
    print(f"  - Objects (cake): {'VERIFIED' if object_found else 'NOT VERIFIED'}")


if __name__ == "__main__":
    run_query_parser_smoke_test()
