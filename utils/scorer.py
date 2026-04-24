"""Weighted scoring system for resume quality and readiness."""

from config import DEFAULT_SCORE_WEIGHTS


QUALITY_SECTIONS = ["education", "skills", "projects"]


def _percentage(value: float) -> float:
    """Keep component values in the 0-100 range."""
    return max(0.0, min(100.0, value))


def calculate_resume_score(text: str, skills: list[str], job_match: dict | None = None) -> dict:
    """Calculate weighted resume score with explainable breakdown."""
    normalized_text = (text or "").lower()
    words = normalized_text.split()
    word_count = len(words)

    skill_score = _percentage(len(skills) * 5)
    project_score = 70.0 if "project" in normalized_text else 30.0
    experience_score = 70.0 if ("intern" in normalized_text or "experience" in normalized_text) else 30.0

    present_sections = sum(1 for section in QUALITY_SECTIONS if section in normalized_text)
    resume_quality_score = _percentage((present_sections / len(QUALITY_SECTIONS)) * 100)

    if word_count == 0 or not skills:
        keyword_density_score = 0.0
    else:
        mentions = sum(normalized_text.count(skill) for skill in skills)
        keyword_density_score = _percentage((mentions / word_count) * 400)

    score = (
        DEFAULT_SCORE_WEIGHTS["skill_score"] * skill_score
        + DEFAULT_SCORE_WEIGHTS["project_score"] * project_score
        + DEFAULT_SCORE_WEIGHTS["experience_score"] * experience_score
        + DEFAULT_SCORE_WEIGHTS["resume_quality_score"] * resume_quality_score
        + DEFAULT_SCORE_WEIGHTS["keyword_density_score"] * keyword_density_score
    )

    explanations = []
    if skill_score < 45:
        explanations.append("Low number of relevant skills detected")
    if project_score <= 30:
        explanations.append("Projects section is weak")
    if experience_score <= 30:
        explanations.append("Experience evidence is limited")
    if resume_quality_score < 65:
        explanations.append("Core sections need better structure")
    if keyword_density_score < 35:
        explanations.append("Important keywords are not repeated naturally")

    missing_skills = []
    if job_match:
        missing_skills = job_match.get("missing_skills", [])

    suggestions = []
    for skill in missing_skills[:4]:
        suggestions.append(f"Learn {skill.title()} -> Practice with one mini project and measurable outcomes")

    if not suggestions:
        suggestions.append("Improve project bullets -> Add tools used, your role, and measurable results")

    if not explanations:
        explanations.append("Strong baseline across key resume components")

    if missing_skills:
        top_missing = ", ".join(skill.title() for skill in missing_skills[:2])
        insight = f"Strong technical base but lacks {top_missing}."
    elif score >= 70:
        insight = "Good beginner profile with balanced core sections."
    else:
        insight = "Good beginner profile but needs project depth."

    return {
        "score": round(score, 2),
        "breakdown": {
            "skill_score": round(skill_score, 2),
            "project_score": round(project_score, 2),
            "experience_score": round(experience_score, 2),
            "resume_quality_score": round(resume_quality_score, 2),
            "keyword_density_score": round(keyword_density_score, 2),
        },
        "explanations": explanations,
        "insight": insight,
        "suggestions": suggestions,
    }
