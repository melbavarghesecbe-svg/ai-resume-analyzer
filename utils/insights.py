"""Insight helpers for readable analysis summaries."""


def build_result_insight(score_data: dict, match_data: dict, predicted_role: str) -> str:
    """Build a short, human-readable analysis summary."""
    score = score_data.get("score", 0)
    missing_skills = match_data.get("missing_skills", [])

    if missing_skills:
        top_missing = ", ".join(skill.title() for skill in missing_skills[:2])
        return f"Strong technical base for {predicted_role}, but missing {top_missing}."

    if score >= 75:
        return f"Strong profile for {predicted_role} with balanced resume quality."

    if score >= 55:
        return f"Good beginner profile for {predicted_role}, but needs project depth."

    return f"Early-stage profile for {predicted_role}; focus on core skills and projects."


def evaluate_target_role_strength(skills: list[str], role_skills: list[str], target_role: str) -> dict:
    """Evaluate resume strength for a selected target role."""
    skill_set = set(skill.lower() for skill in skills)
    role_skill_set = set(skill.lower() for skill in role_skills)

    matched = sorted(role_skill_set.intersection(skill_set))
    missing = sorted(role_skill_set - skill_set)

    strength = 0.0
    if role_skills:
        strength = round((len(matched) / len(role_skills)) * 100, 1)

    if strength > 70:
        level = "Strong"
    elif strength > 40:
        level = "Moderate"
    else:
        level = "Low"

    explanations = [
        f"Matched {len(matched)} of {len(role_skills)} expected skills for {target_role}.",
        f"Target-role strength is {strength}% ({level}).",
    ]

    return {
        "target_role": target_role,
        "strength": strength,
        "level": level,
        "matched_skills": matched,
        "missing_skills": missing,
        "explanations": explanations,
    }
