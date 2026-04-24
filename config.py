"""Central configuration for file paths, thresholds, and scoring weights."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

SKILLS_FILE = DATA_DIR / "skills.json"
ROLES_FILE = DATA_DIR / "roles.json"
ROADMAP_FILE = DATA_DIR / "roadmap.json"

APP_TITLE = "AI Resume Analyzer"

DEFAULT_SCORE_WEIGHTS = {
    "skill_score": 0.4,
    "project_score": 0.2,
    "experience_score": 0.2,
    "resume_quality_score": 0.1,
    "keyword_density_score": 0.1,
}

ROLE_MATCH_THRESHOLD = 0.4

MATCH_LABELS = {
    "strong_min": 70.0,
    "moderate_min": 40.0,
}

IMPORTANT_SKILLS = ["python", "sql", "machine learning"]
QUALITY_SECTIONS = ["education", "skills", "projects"]
