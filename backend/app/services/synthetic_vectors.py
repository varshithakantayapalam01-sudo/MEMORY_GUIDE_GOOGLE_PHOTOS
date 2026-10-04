"""
Deterministic synthetic vector generation.

Used ONLY as a fallback when ALLOW_SYNTHETIC_AI=true (unit tests).
Never used in production or live validation.
"""
from __future__ import annotations
import hashlib
import math


def generate_deterministic_synthetic_vector(text: str, dim: int = 768) -> list[float]:
    """
    Generates a deterministic unit-norm float vector based on text content hash
    when live GEMINI_API_KEY is not configured.
    """
    vector = []
    for i in range(dim):
        seed = f"{text}_{i}".encode("utf-8")
        h = hashlib.sha256(seed).digest()
        val = (int.from_bytes(h[:4], "big") / (2**32 - 1)) * 2.0 - 1.0
        vector.append(val)

    norm = math.sqrt(sum(v * v for v in vector))
    return [v / norm for v in vector] if norm > 0 else vector
