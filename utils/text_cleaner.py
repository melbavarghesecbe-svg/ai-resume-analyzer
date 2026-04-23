"""Text cleaning helpers used across the project."""

import re


def clean_text(text: str) -> str:
    """Return normalized text for consistent matching.

    Steps:
    1. Convert to lowercase.
    2. Remove special characters (keep letters, digits, +, #, and spaces).
    3. Collapse multiple spaces into one.
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9+#\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
