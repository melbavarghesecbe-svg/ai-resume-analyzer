import PyPDF2
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

KEYWORD_SKILLS = [
    "python",
    "java",
    "sql",
    "ml",
    "machine learning",
    "data analysis",
    "pandas",
    "numpy",
    "excel",
    "power bi",
    "tableau",
    "git",
    "html",
    "css",
    "javascript",
    "react",
    "django",
    "flask",
    "aws",
    "communication",
]

SKILL_PRIORITY = {
    "python": 1,
    "java": 1,
    "sql": 1,
    "javascript": 1,
    "react": 1,
    "django": 1,
    "flask": 1,
    "aws": 1,
    "ml": 1,
    "machine learning": 1,
    "data analysis": 2,
    "pandas": 2,
    "numpy": 2,
    "power bi": 2,
    "tableau": 2,
    "git": 2,
    "html": 2,
    "css": 2,
    "excel": 3,
    "communication": 4,
}

ROLE_SKILL_BOOSTS = {
    "frontend": {"javascript", "react", "html", "css", "git"},
    "data": {"sql", "python", "pandas", "numpy", "power bi", "tableau", "excel"},
    "ml": {"python", "ml", "machine learning", "pandas", "numpy", "sql"},
    "backend": {"python", "java", "django", "flask", "sql", "aws", "git"},
}


def extract_skills_from_text(text):
    if not text:
        return []

    normalized_text = text.lower()
    detected_skills = []

    for skill in KEYWORD_SKILLS:
        if skill in normalized_text:
            detected_skills.append(skill)

    return detected_skills


def detect_job_focus(job_text):
    text = (job_text or "").lower()
    if any(keyword in text for keyword in ["frontend", "front-end", "react", "javascript", "ui", "css", "html"]):
        return "frontend"
    if any(keyword in text for keyword in ["data analyst", "analytics", "power bi", "tableau", "sql", "excel"]):
        return "data"
    if any(keyword in text for keyword in ["machine learning", "ml", "model", "ai"]):
        return "ml"
    if any(keyword in text for keyword in ["backend", "back-end", "api", "django", "flask", "microservice"]):
        return "backend"
    return None


def rank_recommended_skills(missing_skills, job_text=""):
    # Lower numeric values represent higher recommendation priority.
    focus = detect_job_focus(job_text)
    boosted_skills = ROLE_SKILL_BOOSTS.get(focus, set())
    return sorted(
        missing_skills,
        key=lambda skill: (0 if skill in boosted_skills else 1, SKILL_PRIORITY.get(skill, 99), skill),
    )

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def analyze_resume(text):
    if not text or not text.strip():
        return {
            "skills": [],
            "score": 0,
            "suggestions": ["Add resume content so your skills can be analyzed."],
            "role": "General Tech Role",
            "breakdown": {
                "skills": 0,
                "projects": 0,
                "experience": 0,
            },
        }

    normalized_text = text.lower()
    detected_skills = extract_skills_from_text(text)

    has_project = "project" in normalized_text
    has_internship = "internship" in normalized_text
    has_team = "team" in normalized_text
    has_leadership = any(
        word in normalized_text for word in ["leader", "leadership", "captain", "managed", "mentored"]
    )

    # Breakdown scores (all normalized to a 0-10 scale).
    skills_score = min(len(detected_skills), 10)
    project_score = 10 if has_project else 0

    experience_points = 0
    if has_internship:
        experience_points += 4
    if has_team:
        experience_points += 3
    if has_leadership:
        experience_points += 3
    experience_score = min(experience_points, 10)

    # Final score combines the three sections and remains 0-10.
    score = int(round((skills_score + project_score + experience_score) / 3))

    if "ml" in detected_skills or "machine learning" in detected_skills:
        role = "Machine Learning Engineer"
    elif any(skill in detected_skills for skill in ["react", "html", "css"]):
        role = "Frontend Developer"
    elif any(skill in detected_skills for skill in ["sql", "data analysis", "pandas", "numpy", "excel", "power bi", "tableau"]):
        role = "Data Analyst"
    elif "python" in detected_skills:
        role = "Software Developer"
    else:
        role = "General Tech Role"

    suggestions = []
    if "python" not in detected_skills:
        suggestions.append("Learn Python and add beginner-to-intermediate Python projects.")
    if "ml" not in detected_skills and "machine learning" not in detected_skills:
        suggestions.append("Learn Machine Learning basics and include one ML project.")
    if len(detected_skills) < 5:
        suggestions.append("Add more technical and soft skills to strengthen your resume.")
    if "project" not in normalized_text:
        suggestions.append("Add at least one project to strengthen your resume.")
    if "internship" not in normalized_text:
        suggestions.append("Try to include internship or practical work experience.")
    if not has_leadership and not has_team:
        suggestions.append("Highlight leadership or teamwork examples from your work.")
    if not suggestions:
        suggestions.append("Great profile. Keep building projects and quantifying your impact.")

    return {
        "skills": detected_skills,
        "score": score,
        "suggestions": suggestions,
        "role": role,
        "breakdown": {
            "skills": skills_score,
            "projects": project_score,
            "experience": experience_score,
        },
    }


def match_job_description(resume_text, job_text):
    resume_skills = extract_skills_from_text(resume_text)
    job_skills = extract_skills_from_text(job_text)

    matched_skills = []
    missing_skills = []

    for skill in job_skills:
        if skill in resume_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    if len(job_skills) == 0:
        match_percentage = 0
    else:
        match_percentage = int((len(matched_skills) / len(job_skills)) * 100)

    recommended_skills = rank_recommended_skills(missing_skills, job_text)[:5]

    return {
        "match_percentage": match_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommended_skills": recommended_skills,
    }


def generate_pdf_report(result):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
    y_position = height - 125

    def draw_header():
        pdf.setFillColor(colors.HexColor("#0F172A"))
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(48, height - 42, "Resume Intelligence Studio")

        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(colors.HexColor("#475569"))
        pdf.drawString(48, height - 58, "AI Career Analysis Report")

        report_date = datetime.now().strftime("%B %d, %Y")
        pdf.drawRightString(width - 48, height - 58, report_date)

        pdf.setStrokeColor(colors.HexColor("#D1D5DB"))
        pdf.line(48, height - 68, width - 48, height - 68)

    def draw_footer():
        pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
        pdf.line(48, 44, width - 48, 44)
        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(width / 2, 30, "Generated by Resume Intelligence Studio")

    def start_new_page():
        nonlocal y_position
        draw_footer()
        pdf.showPage()
        draw_header()
        y_position = height - 125

    def ensure_space(required_space):
        if y_position < required_space:
            start_new_page()

    def draw_section_title(title):
        nonlocal y_position
        ensure_space(100)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.setFillColor(colors.HexColor("#0F4C81"))
        pdf.drawString(48, y_position, title)
        y_position -= 20

    def draw_bullet_list(items):
        nonlocal y_position
        if not items:
            items = ["No items available."]
        pdf.setFont("Helvetica", 11)
        pdf.setFillColor(colors.HexColor("#1F2937"))
        for item in items:
            ensure_space(80)
            pdf.drawString(60, y_position, f"- {item}")
            y_position -= 16

    draw_header()

    # Title
    pdf.setFont("Helvetica-Bold", 19)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.drawString(48, y_position, "Resume Analysis Report")
    y_position -= 28

    # Score highlight
    score = result.get("score", 0)
    ensure_space(140)
    pdf.setFillColor(colors.HexColor("#ECFEFF"))
    pdf.setStrokeColor(colors.HexColor("#A5F3FC"))
    pdf.roundRect(48, y_position - 32, width - 96, 44, 8, stroke=1, fill=1)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(60, y_position - 14, f"Resume Score: {score} / 10")
    y_position -= 58

    # Skills section
    draw_section_title("Skills")
    skills = [skill.title() for skill in result.get("skills", [])]
    draw_bullet_list(skills)
    y_position -= 12

    # Suggestions section
    draw_section_title("Suggestions")
    suggestions = result.get("suggestions", [])
    draw_bullet_list(suggestions)
    y_position -= 12

    # Job match section (optional)
    job_match = result.get("job_match")
    if isinstance(job_match, dict):
        draw_section_title("Job Match")
        match_percentage = job_match.get("match_percentage", 0)
        draw_bullet_list([f"Match Percentage: {match_percentage}%"])
        y_position -= 8

        matched_skills = [skill.title() for skill in job_match.get("matched_skills", [])]
        draw_section_title("Matching Skills")
        draw_bullet_list(matched_skills)
        y_position -= 8

        missing_skills = [skill.title() for skill in job_match.get("missing_skills", [])]
        draw_section_title("Missing Skills")
        draw_bullet_list(missing_skills)

        recommended_skills = [skill.title() for skill in job_match.get("recommended_skills", [])]
        draw_section_title("Recommended Skills to Learn")
        draw_bullet_list(recommended_skills)

    draw_footer()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()