"""Professional PDF report generation using ReportLab Platypus."""

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _build_styles():
    """Create readable custom styles for a structured professional report."""
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=colors.HexColor("#0F4C81"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CardLabel",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=colors.HexColor("#475569"),
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CardValue",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=colors.HexColor("#0F172A"),
            alignment=TA_CENTER,
        )
    )
    return styles


def _to_bullets(items: list[str]) -> str:
    """Convert list values to simple HTML bullets for Paragraph rendering."""
    if not items:
        return "- No data available"
    return "<br/>".join(f"- {item}" for item in items)


def _metric_cards(styles, score: float, role: str, match_text: str) -> Table:
    """Build a simple 3-card metric summary row."""
    card_data = [
        [
            Paragraph("Resume Score", styles["CardLabel"]),
            Paragraph("Predicted Role", styles["CardLabel"]),
            Paragraph("Job Match", styles["CardLabel"]),
        ],
        [
            Paragraph(f"{score} / 100", styles["CardValue"]),
            Paragraph(role, styles["CardValue"]),
            Paragraph(match_text, styles["CardValue"]),
        ],
    ]

    cards = Table(card_data, colWidths=[2.1 * inch, 2.1 * inch, 2.1 * inch])
    cards.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return cards


def generate_pdf(data: dict) -> bytes:
    """Generate a polished PDF with hierarchy, tables, and actionable sections."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = _build_styles()
    content = []

    score = data.get("score", 0)
    role = data.get("role", "General Tech Role")
    match_percentage = data.get("match_percentage", 0)
    match_level = data.get("match_level", "Low Match")
    role_confidence = data.get("role_confidence", {})

    detected_skills = [skill.title() for skill in data.get("skills", [])]
    missing_skills = [skill.title() for skill in data.get("missing_skills", [])]
    suggestions = data.get("suggestions", [])
    key_insight = data.get("key_insight", "Profile has growth potential with targeted skill improvements.")
    breakdown = data.get("breakdown", {})

    # Branded title strip.
    title_strip = Table(
        [[
            Paragraph("<b>AI Resume Analysis Report</b>", styles["Title"]),
            Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles["Body"]),
        ]],
        colWidths=[4.2 * inch, 2.1 * inch],
    )
    title_strip.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF4FF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#BFD2F4")),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    content.append(title_strip)
    content.append(Spacer(1, 12))

    content.append(_metric_cards(styles, score, role, f"{match_percentage}% ({match_level})"))
    content.append(Spacer(1, 12))

    content.append(Paragraph("1. Candidate Summary", styles["SectionHeading"]))
    content.append(Paragraph(key_insight, styles["Body"]))
    content.append(Spacer(1, 8))

    content.append(Paragraph("2. Role Prediction Confidence", styles["SectionHeading"]))
    if role_confidence:
        confidence_rows = [["Role", "Confidence"]]
        for role_name, confidence in sorted(role_confidence.items(), key=lambda item: item[1], reverse=True):
            confidence_rows.append([role_name, f"{confidence}%"])

        confidence_table = Table(confidence_rows, colWidths=[4.8 * inch, 1.5 * inch])
        confidence_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        content.append(confidence_table)
    else:
        content.append(Paragraph("Role confidence data not available.", styles["Body"]))
    content.append(Spacer(1, 8))

    content.append(Paragraph("3. Skills Overview", styles["SectionHeading"]))
    content.append(Paragraph("<b>Detected Skills</b>", styles["Body"]))
    content.append(Paragraph(_to_bullets(detected_skills), styles["Body"]))
    content.append(Spacer(1, 6))
    content.append(Paragraph("<b>Missing Skills</b>", styles["Body"]))
    content.append(Paragraph(_to_bullets(missing_skills), styles["Body"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph("4. Score Breakdown", styles["SectionHeading"]))
    table_data = [
        ["Metric", "Score"],
        ["Skills", f"{breakdown.get('skill_score', 0)}%"],
        ["Projects", f"{breakdown.get('project_score', 0)}%"],
        ["Experience", f"{breakdown.get('experience_score', 0)}%"],
        ["Resume Quality", f"{breakdown.get('resume_quality_score', 0)}%"],
        ["Keyword Density", f"{breakdown.get('keyword_density_score', 0)}%"],
    ]

    table = Table(table_data, colWidths=[3.1 * inch, 2.2 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.HexColor("#EEF2FF")]),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    content.append(table)
    content.append(Spacer(1, 10))

    content.append(Paragraph("5. Recommendations", styles["SectionHeading"]))
    content.append(Paragraph(_to_bullets(suggestions), styles["Body"]))

    document.build(content)
    buffer.seek(0)
    return buffer.getvalue()
