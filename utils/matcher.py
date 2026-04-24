"""Job description matching logic with weighted skills."""

import json
from functools import lru_cache

from config import IMPORTANT_SKILLS, ROADMAP_FILE
from utils.skill_extractor import extract_skills


@lru_cache(maxsize=1)
def _load_roadmap_guidance() -> dict[str, str]:
    """Load roadmap guidance from JSON with fallback defaults."""
    try:
        with open(ROADMAP_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return {str(key).lower(): str(value) for key, value in data.items()}
    except Exception:
        pass

    return {
        "sql": "Practice joins and aggregations on datasets",
        "python": "Build one mini automation project",
        "machine learning": "Train one baseline model and explain metrics",
    }


def _weight(skill: str) -> int:
    """Assign weight 2 for important skills and 1 for others."""
    return 2 if skill.lower() in {s.lower() for s in IMPORTANT_SKILLS} else 1


def _match_level(match_percentage: float) -> str:
    """Map percentage to label."""
    if match_percentage > 70:
        return "Strong"
    if match_percentage > 40:
        return "Moderate"
    return "Low"


def match_resume_to_job(resume_text: str, job_text: str) -> dict:
    """Compare resume and job description using weighted skill overlap."""
    if not job_text or not job_text.strip():
        return {
            "matched_skills": [],
            "missing_skills": [],
            "match_percentage": 0.0,
            "match_level": "Low",
            "job_skills": [],
            "explanations": ["Job description not provided, so JD match was skipped."],
        }

    resume_skills = set(extract_skills(resume_text))
    job_skills = sorted(set(extract_skills(job_text)))

    matched_skills = sorted(skill for skill in job_skills if skill in resume_skills)
    missing_skills = sorted(skill for skill in job_skills if skill not in resume_skills)

    total_weight = sum(_weight(skill) for skill in job_skills)
    matched_weight = sum(_weight(skill) for skill in matched_skills)

    match_percentage = 0.0
    if total_weight > 0:
        match_percentage = round((matched_weight / total_weight) * 100, 1)

    level = _match_level(match_percentage)

    explanations = [
        f"Matched {len(matched_skills)} out of {len(job_skills)} detected job skills.",
        f"Weighted overlap gives {match_percentage}% match ({level}).",
    ]

    if missing_skills:
        top_missing = ", ".join(skill.title() for skill in missing_skills[:3])
        explanations.append(f"Top missing skills: {top_missing}.")

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": round(match_percentage, 1),
        "match_level": level,
        "job_skills": job_skills,
        "explanations": explanations,
    }


def build_skill_gap_roadmap(missing_skills: list[str]) -> list[str]:
    """Generate actionable roadmap suggestions."""
    if not missing_skills:
        return ["Great job. You currently match the listed job skills well."]

    roadmap_lookup = _load_roadmap_guidance()
    roadmap = []
    for skill in missing_skills[:6]:
        guidance = roadmap_lookup.get(skill.lower(), "Build one small project to demonstrate practical use")
        roadmap.append(f"Learn {skill.title()} -> {guidance}")

    return roadmap
