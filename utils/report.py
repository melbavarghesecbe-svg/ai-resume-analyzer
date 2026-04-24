"""PDF report generation for resume analysis."""

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _bullet_lines(items: list[str]) -> str:
    """Convert list values into simple line-bullet HTML."""
    if not items:
        return "- Not available"
    return "<br/>".join(f"- {item}" for item in items)


def _build_summary_table(score: float, role: str, match_percentage: float) -> Table:
    """Build top summary table for key report metrics."""
    table = Table(
        [
            ["Overall Score", f"{score} / 100"],
            ["Predicted Role", role],
            ["Job Match", f"{match_percentage}%"],
        ],
        colWidths=[180, 320],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF2FF")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _build_breakdown_table(breakdown: dict) -> Table:
    """Build score breakdown table."""
    breakdown_rows = [["Metric", "Score"]]
    for key, value in breakdown.items():
        breakdown_rows.append([key.replace("_", " ").title(), f"{value}%"])

    table = Table(breakdown_rows, colWidths=[260, 240])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    return table


def generate_pdf(data: dict) -> bytes:
    """Create a clean report with score, role, match, breakdown, skills, and recommendations."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    score = data.get("score", 0)
    role = data.get("role", "General Tech Role")
    match_percentage = data.get("match_percentage", 0)
    breakdown = data.get("breakdown", {})
    skills = [skill.title() for skill in data.get("skills", [])]
    missing_skills = [skill.title() for skill in data.get("missing_skills", [])]
    suggestions = data.get("suggestions", [])
    insight = data.get("insight", "")

    story.append(Paragraph("AI Resume Analyzer Report", styles["Title"]))
    story.append(Spacer(1, 8))

    story.append(_build_summary_table(score, role, match_percentage))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Insight", styles["Heading2"]))
    story.append(Paragraph(insight or "No summary insight available.", styles["BodyText"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Score Breakdown", styles["Heading2"]))
    story.append(_build_breakdown_table(breakdown))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Detected Skills", styles["Heading2"]))
    story.append(Paragraph(_bullet_lines(skills), styles["BodyText"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Missing Skills", styles["Heading2"]))
    story.append(Paragraph(_bullet_lines(missing_skills), styles["BodyText"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Recommendations", styles["Heading2"]))
    story.append(Paragraph(_bullet_lines(suggestions), styles["BodyText"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
