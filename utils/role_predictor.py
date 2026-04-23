"""Role prediction based on overlap between detected skills and role skill maps."""

import json
from functools import lru_cache

from config import ROLES_FILE


@lru_cache(maxsize=1)
def _load_role_map() -> dict[str, list[str]]:
    """Load role-to-skills mapping from JSON once per process."""
    with open(ROLES_FILE, "r", encoding="utf-8") as file:
        role_map = json.load(file)

    return {role: [skill.lower() for skill in skills] for role, skills in role_map.items()}


def get_role_skills(role_name: str) -> list[str]:
    """Return the skill list associated with a role."""
    return _load_role_map().get(role_name, [])


def get_role_confidence(skills: list[str]) -> dict[str, float]:
    """Return normalized confidence scores for each role.

    Confidence is computed as:
        overlap_with_role_skills / number_of_role_skills * 100
    """
    if not skills:
        return {role: 0.0 for role in _load_role_map()}

    skill_set = set(skill.lower() for skill in skills)
    confidence_scores = {}

    for role, role_skills in _load_role_map().items():
        if not role_skills:
            confidence_scores[role] = 0.0
            continue

        overlap = len(skill_set.intersection(role_skills))
        confidence_scores[role] = round((overlap / len(role_skills)) * 100, 1)

    return confidence_scores


def predict_role(skills: list[str]) -> str:
    """Predict the best matching role from detected resume skills.

    The score for each role is normalized overlap:
        overlap / number_of_role_skills
    A minimum threshold is used to avoid overconfident predictions.
    """
    role_confidence = get_role_confidence(skills)
    if not role_confidence:
        return "General Tech Role"

    best_role, best_percent = max(role_confidence.items(), key=lambda item: item[1])
    best_score = best_percent / 100

    # If role confidence is too low, avoid a misleading specialized label.
    if best_score < 0.4:
        return "General Tech Role"

    return best_role
