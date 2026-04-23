"""Weighted scoring system for resume quality and readiness."""

from config import DEFAULT_SCORE_WEIGHTS


PROJECT_KEYWORDS = ["project", "capstone", "portfolio", "built", "developed"]
EXPERIENCE_KEYWORDS = ["experience", "internship", "worked", "team", "led", "managed"]
QUALITY_SECTIONS = ["summary", "skills", "experience", "project", "education"]


def _percentage(value: float) -> float:
    """Keep component values in the 0-100 range."""
    return max(0.0, min(100.0, value))


def calculate_resume_score(text: str, skills: list[str], job_match: dict | None = None) -> dict:
    """Calculate weighted resume score and improvement suggestions.

    Formula:
        score =
            0.4 * skill_score +
            0.2 * project_score +
            0.2 * experience_score +
            0.1 * resume_quality_score +
            0.1 * keyword_density_score
    """
    normalized_text = (text or "").lower()
    words = normalized_text.split()
    word_count = len(words)

    # 1) Skill strength: each relevant skill contributes 5 points.
    skill_score = _percentage(len(skills) * 5)

    # 2) Project strength baseline: resumes with project evidence score higher.
    project_score = 50.0 if "project" in normalized_text else 20.0
    project_hits = sum(1 for keyword in PROJECT_KEYWORDS if keyword in normalized_text)
    if project_hits >= 3:
        project_score = _percentage(project_score + 20)

    # 3) Experience strength baseline: internship and work signals matter.
    experience_score = 60.0 if ("intern" in normalized_text or "internship" in normalized_text) else 30.0
    experience_hits = sum(1 for keyword in EXPERIENCE_KEYWORDS if keyword in normalized_text)
    if experience_hits >= 3:
        experience_score = _percentage(experience_score + 20)

    # 4) Resume quality: checks whether core sections are present.
    quality_sections = ["education", "skills", "projects"]
    present_sections = sum(1 for section in quality_sections if section in normalized_text)
    resume_quality_score = _percentage(present_sections * 33)

    # 5) Keyword density: higher score when important terms are repeated naturally.
    if word_count == 0 or not skills:
        keyword_density_score = 0.0
    else:
        mentions = sum(normalized_text.count(skill) for skill in skills)
        keyword_density_score = _percentage((mentions / word_count) * 200)

    score = (
        DEFAULT_SCORE_WEIGHTS["skill_score"] * skill_score
        + DEFAULT_SCORE_WEIGHTS["project_score"] * project_score
        + DEFAULT_SCORE_WEIGHTS["experience_score"] * experience_score
        + DEFAULT_SCORE_WEIGHTS["resume_quality_score"] * resume_quality_score
        + DEFAULT_SCORE_WEIGHTS["keyword_density_score"] * keyword_density_score
    )

    suggestions = []
    if skill_score < 55:
        suggestions.append("Add more relevant technical skills for your target role.")
    if project_score < 50:
        suggestions.append("Add project details with tools used and measurable outcomes.")
    if experience_score < 50:
        suggestions.append("Highlight internships, teamwork, and real-world experience.")
    if resume_quality_score < 60:
        suggestions.append("Use clear sections like Summary, Skills, Experience, and Projects.")
    if keyword_density_score < 45:
        suggestions.append("Repeat important skills naturally in project and experience bullets.")

    if job_match and job_match.get("missing_skills"):
        top_missing = ", ".join(skill.title() for skill in job_match["missing_skills"][:4])
        suggestions.append(f"Close job gaps by learning: {top_missing}.")

    if not suggestions:
        suggestions.append("Strong resume foundation. Keep improving impact-focused bullet points.")

    return {
        "score": round(score, 2),
        "breakdown": {
            "skill_score": round(skill_score, 2),
            "project_score": round(project_score, 2),
            "experience_score": round(experience_score, 2),
            "resume_quality_score": round(resume_quality_score, 2),
            "keyword_density_score": round(keyword_density_score, 2),
        },
        "suggestions": suggestions,
    }
