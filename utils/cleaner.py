"""Text normalization helpers used across the app."""

import re


def normalize_text(text: str) -> str:
    """Lowercase and remove noisy characters while preserving + and #."""
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9+#\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_words(text: str) -> list[str]:
    """Return normalized word tokens for simple matching logic."""
    normalized = normalize_text(text)
    if not normalized:
        return []
    return normalized.split()
