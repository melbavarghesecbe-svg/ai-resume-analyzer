"""Skill extraction logic using a curated keyword list."""

import json
from functools import lru_cache

from config import SKILLS_FILE
from utils.text_cleaner import clean_text

# Basic synonym mapping requested in the project requirements.
SYNONYM_MAP = {
    "js": "javascript",
    "ml": "machine learning",
    "py": "python",
}


@lru_cache(maxsize=1)
def _load_skills() -> list[str]:
    """Load skill keywords from JSON only once for performance."""
    with open(SKILLS_FILE, "r", encoding="utf-8") as file:
        skills = json.load(file)

    # Normalize once so extraction logic stays simple and consistent.
    return sorted({clean_text(skill) for skill in skills if clean_text(skill)})


def _normalize_with_synonyms(text: str) -> str:
    """Normalize text and replace known short aliases with canonical names."""
    normalized = clean_text(text)
    tokens = [SYNONYM_MAP.get(token, token) for token in normalized.split()]
    return " ".join(tokens)


def extract_skills(text: str) -> list[str]:
    """Extract single-word and multi-word skills from text.

    This function supports exact token matching for single words and
    phrase matching for skills like "machine learning" and "data analysis".
    """
    if not text:
        return []

    normalized_text = _normalize_with_synonyms(text)
    token_set = set(normalized_text.split())
    padded_text = f" {normalized_text} "

    detected = []
    for skill in _load_skills():
        if " " in skill:
            if f" {skill} " in padded_text:
                detected.append(skill)
        else:
            if skill in token_set:
                detected.append(skill)

    return sorted(set(detected))
