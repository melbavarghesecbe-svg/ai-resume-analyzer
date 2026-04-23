"""Job description matching logic with weighted skills."""

import re

from utils.skill_extractor import extract_skills

IMPORTANT_MARKERS = {
    "must",
    "required",
    "mandatory",
    "strong",
    "expert",
    "proficient",
    "hands on",
}

ROADMAP_GUIDANCE = {
    "sql": "Practice SELECT, JOIN, and GROUP BY using real datasets.",
    "pandas": "Build a mini data analysis project using CSV datasets.",
    "numpy": "Practice arrays, indexing, and vectorized operations on sample data.",
    "excel": "Learn pivot tables, lookups, and basic analytics dashboards.",
    "data visualization": "Create clear charts and dashboards from one business dataset.",
    "power bi": "Build an interactive dashboard with filters and KPI cards.",
    "tableau": "Create a dashboard story with insights and trends.",
    "communication": "Add quantified achievements and clear project impact statements in your resume.",
    "machine learning": "Train one end-to-end ML model and explain metrics and trade-offs.",
    "python": "Solve beginner-to-intermediate coding problems and automate one task.",
}


def _split_sentences(text: str) -> list[str]:
    """Split text into small sentence-like chunks for marker lookup."""
    if not text:
        return []
    return [chunk.strip() for chunk in re.split(r"[\n\.!?]+", text.lower()) if chunk.strip()]


def _build_job_skill_weights(job_text: str, job_skills: list[str]) -> dict[str, float]:
    """Assign higher weights to skills that look important in the JD.

    A skill gets extra weight when it appears near words such as
    "required" or "must".
    """
    weights = {skill: 1.0 for skill in job_skills}
    if not job_text:
        return weights

    lower_text = job_text.lower()
    sentences = _split_sentences(lower_text)

    for skill in job_skills:
        mentions = lower_text.count(skill)
        if mentions > 1:
            weights[skill] += 0.3

        for sentence in sentences:
            if skill in sentence and any(marker in sentence for marker in IMPORTANT_MARKERS):
                weights[skill] = max(weights[skill], 2.0)

    return weights


def match_resume_to_job(resume_text: str, job_text: str) -> dict:
    """Compare resume and job description using weighted skill overlap."""
    if not job_text or not job_text.strip():
        return {
            "matched_skills": [],
            "missing_skills": [],
            "match_percentage": 0,
            "match_level": "Low Match",
            "job_skills": [],
            "skill_weights": {},
        }

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    resume_skill_set = set(resume_skills)
    matched_skills = [skill for skill in job_skills if skill in resume_skill_set]
    missing_skills = [skill for skill in job_skills if skill not in resume_skill_set]

    skill_weights = _build_job_skill_weights(job_text, job_skills)
    total_weight = sum(skill_weights.values())
    matched_weight = sum(skill_weights[skill] for skill in matched_skills)

    match_percentage = 0
    if total_weight > 0:
        match_percentage = round((matched_weight / total_weight) * 100, 1)

    if match_percentage > 70:
        match_level = "Strong Match"
    elif match_percentage > 40:
        match_level = "Moderate Match"
    else:
        match_level = "Low Match"

    return {
        "matched_skills": sorted(set(matched_skills)),
        "missing_skills": sorted(set(missing_skills)),
        "match_percentage": match_percentage,
        "match_level": match_level,
        "job_skills": sorted(set(job_skills)),
        "skill_weights": skill_weights,
    }


def build_skill_gap_roadmap(missing_skills: list[str]) -> list[str]:
    """Generate a beginner-friendly roadmap from missing skills."""
    if not missing_skills:
        return ["Great job. You currently match the listed job skills well."]

    roadmap = []
    for skill in missing_skills[:6]:
        guidance = ROADMAP_GUIDANCE.get(skill.lower())
        if guidance:
            roadmap.append(f"Learn {skill.title()} -> {guidance}")
        else:
            roadmap.append(f"Learn {skill.title()} -> Build one small project to demonstrate practical use.")

    return roadmap
