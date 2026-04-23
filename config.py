"""Central configuration values for the Resume Analyzer app."""

from pathlib import Path

# Absolute project path so utility modules can safely load data files.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

SKILLS_FILE = DATA_DIR / "skills.json"
ROLES_FILE = DATA_DIR / "roles.json"

APP_TITLE = "AI Resume Analyzer"
DEFAULT_SCORE_WEIGHTS = {
    "skill_score": 0.4,
    "project_score": 0.2,
    "experience_score": 0.2,
    "resume_quality_score": 0.1,
    "keyword_density_score": 0.1,
}
