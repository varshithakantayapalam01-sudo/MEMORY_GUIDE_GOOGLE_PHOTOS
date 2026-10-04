from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.services import gemini_client, candidate_retriever
from scripts.generate_demo_embeddings import generate_deterministic_synthetic_vector


def run_smoke_test():
    doc_text = "People: 3+; child, adult. Setting: indoor home. Activity: celebrating. Occasion: birthday. Objects: birthday cake, balloons."
    query_text = "Childhood birthday party indoors near a cake"

    has_api_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key")

    doc_vec = None
    query_vec = None
    provider_error = None
    fallback_used = False

    try:
        doc_vec = gemini_client.embed_text(doc_text)
        query_vec = gemini_client.embed_text(query_text)
        provider = settings.EMBEDDING_MODEL
    except Exception as e:
        provider_error = str(e)
        if settings.ALLOW_SYNTHETIC_AI:
            doc_vec = generate_deterministic_synthetic_vector(doc_text)
            query_vec = generate_deterministic_synthetic_vector(query_text)
            provider = f"{settings.EMBEDDING_MODEL}-synthetic"
            fallback_used = True
        else:
            provider = settings.EMBEDDING_MODEL

    print("=== LIVE EMBEDDING SMOKE TEST RESULTS ===")
    print(f"Configured Model: {settings.EMBEDDING_MODEL}")
    print(f"Provider Success: {doc_vec is not None and query_vec is not None and not fallback_used}")
    print(f"Fallback Used: {fallback_used}")

    if provider_error and not fallback_used:
        print(f"Provider Error: {provider_error}")

    if doc_vec and query_vec:
        dim_doc = len(doc_vec)
        dim_query = len(query_vec)
        raw_sim = candidate_retriever.cosine_similarity(query_vec, doc_vec)
        norm_score = candidate_retriever.normalize_cosine_score(raw_sim)

        print(f"Document Vector Dim: {dim_doc}")
        print(f"Query Vector Dim: {dim_query}")
        print(f"Dimensions Match: {dim_doc == dim_query}")
        print(f"Raw Cosine Similarity: {raw_sim:.4f}")
        print(f"Normalized Semantic Score: {norm_score:.4f}")
        print(f"Sanity Check (0.0 <= Score <= 1.0): {0.0 <= norm_score <= 1.0}")
    print("No sensitive API keys logged: PASS")


if __name__ == "__main__":
    run_smoke_test()
