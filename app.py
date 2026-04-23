"""Streamlit entry point for the AI Resume Analyzer project."""

import io

import streamlit as st

from config import APP_TITLE
from utils.matcher import build_skill_gap_roadmap, match_resume_to_job
from utils.parser import extract_text_from_pdf
from utils.report import generate_pdf
from utils.role_predictor import get_role_confidence, predict_role
from utils.scorer import calculate_resume_score
from utils.skill_extractor import extract_skills

st.set_page_config(page_title=APP_TITLE, layout="wide")


def apply_theme(theme_name: str) -> None:
    """Apply a basic light/dark theme using custom CSS."""
    if theme_name == "Dark":
        st.markdown(
            """
            <style>
            .stApp {background: #0f172a; color: #e2e8f0;}
            section[data-testid="stSidebar"] {background: #111827;}
            div[data-testid="stMetric"] {background: #1f2937; padding: 8px; border-radius: 10px;}
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            .stApp {background: #f8fafc; color: #0f172a;}
            section[data-testid="stSidebar"] {background: #e2e8f0;}
            div[data-testid="stMetric"] {background: #ffffff; padding: 8px; border-radius: 10px;}
            </style>
            """,
            unsafe_allow_html=True,
        )


@st.cache_data(show_spinner=False)
def analyze_resume_file(file_bytes: bytes, job_description: str) -> dict:
    """Run the full analysis pipeline for one resume file."""
    resume_text = extract_text_from_pdf(io.BytesIO(file_bytes))
    if not resume_text:
        return {"error": "No extractable text found in this PDF. Please upload a clearer resume."}

    skills = extract_skills(resume_text)
    role_confidence = get_role_confidence(skills)
    predicted_role = predict_role(skills)

    job_match = match_resume_to_job(resume_text, job_description)
    score_data = calculate_resume_score(
        resume_text,
        skills,
        job_match=job_match if job_description.strip() else None,
    )

    roadmap = build_skill_gap_roadmap(job_match.get("missing_skills", [])) if job_description.strip() else []

    key_insight = "Your profile shows strong fundamentals and is ready for targeted improvements."
    if job_description.strip() and job_match.get("missing_skills"):
        top_missing = ", ".join(skill.title() for skill in job_match["missing_skills"][:3])
        key_insight = (
            "Your profile shows strong programming fundamentals but lacks core skills for this role: "
            f"{top_missing}."
        )

    report_payload = {
        "role": predicted_role,
        "score": score_data["score"],
        "match_percentage": job_match["match_percentage"],
        "match_level": job_match.get("match_level", "Low Match"),
        "role_confidence": role_confidence,
        "skills": skills,
        "missing_skills": job_match["missing_skills"],
        "suggestions": score_data["suggestions"],
        "breakdown": score_data["breakdown"],
        "key_insight": key_insight,
    }

    return {
        "resume_text": resume_text,
        "skills": skills,
        "role": predicted_role,
        "role_confidence": role_confidence,
        "job_match": job_match,
        "score": score_data,
        "roadmap": roadmap,
        "key_insight": key_insight,
        "pdf_bytes": generate_pdf(report_payload),
    }


@st.cache_data(show_spinner=False)
def quick_resume_summary(file_bytes: bytes) -> dict:
    """Generate a quick score/role summary used by resume comparison."""
    resume_text = extract_text_from_pdf(io.BytesIO(file_bytes))
    if not resume_text:
        return {"error": "No extractable text found."}

    skills = extract_skills(resume_text)
    role = predict_role(skills)
    score_data = calculate_resume_score(resume_text, skills)

    return {
        "role": role,
        "score": score_data["score"],
        "skills": skills,
    }


def render_breakdown(breakdown: dict) -> None:
    """Render each weighted score component as a progress bar."""
    labels = {
        "skill_score": "Skill Score",
        "project_score": "Project Score",
        "experience_score": "Experience Score",
        "resume_quality_score": "Resume Quality Score",
        "keyword_density_score": "Keyword Density Score",
    }

    for key, label in labels.items():
        value = breakdown.get(key, 0)
        st.write(f"{label}: {value}%")
        st.progress(min(max(value / 100, 0.0), 1.0))


def render_analyzer_page() -> None:
    """Render the main resume analyzer workflow."""
    st.subheader("Analyze Resume")
    uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"], key="main_uploader")
    job_description = st.text_area("Paste Job Description (optional)", height=150)

    if st.button("Analyze Resume", type="primary"):
        if not uploaded_file:
            st.error("Please upload a resume PDF before analysis.")
            return

        with st.spinner("Analyzing resume..."):
            result = analyze_resume_file(uploaded_file.getvalue(), job_description)

        if "error" in result:
            st.error(result["error"])
            return

        score = result["score"]["score"]
        st.success("Analysis completed successfully.")

        left_col, right_col = st.columns(2)
        with left_col:
            st.metric("Weighted Resume Score", f"{score} / 100")
            st.progress(min(max(score / 100, 0.0), 1.0))
            st.metric("Predicted Role", result["role"])

        with right_col:
            match_percentage = result["job_match"]["match_percentage"] if job_description.strip() else 0
            st.metric("Job Match", f"{match_percentage}%")
            st.metric("Detected Skills", len(result["skills"]))

        st.subheader("Key Insight")
        st.info(result["key_insight"])

        st.subheader("Role Confidence Panel")
        confidence_rows = [
            {"Role": role_name, "Confidence (%)": confidence}
            for role_name, confidence in sorted(
                result["role_confidence"].items(), key=lambda item: item[1], reverse=True
            )
        ]
        st.table(confidence_rows)

        st.subheader("Skills Overview")
        st.write("### Detected Skills")
        if result["skills"]:
            st.success(", ".join(skill.title() for skill in result["skills"]))
        else:
            st.warning("No skills detected. Please verify your PDF text is selectable.")

        if job_description.strip():
            st.write("### Missing Skills")
            missing_skills = result["job_match"]["missing_skills"]
            if missing_skills:
                st.error(", ".join(skill.title() for skill in missing_skills))
            else:
                st.success("No missing skills found for this job description.")

            st.write("### Job Match Level")
            match_level = result["job_match"].get("match_level", "Low Match")
            st.progress(min(max(result["job_match"]["match_percentage"] / 100, 0.0), 1.0))
            st.write(f"Match: {result['job_match']['match_percentage']}% ({match_level})")

            st.subheader("Skill Gap Roadmap")
            for step in result["roadmap"]:
                st.write(f"- {step}")
        else:
            st.info("Add a job description to see match percentage and missing skills.")

        st.subheader("Recommendations")
        for suggestion in result["score"]["suggestions"]:
            st.write(f"- {suggestion}")

        st.subheader("Score Breakdown")
        render_breakdown(result["score"]["breakdown"])

        st.download_button(
            label="Download PDF Report",
            data=result["pdf_bytes"],
            file_name="resume_analysis_report.pdf",
            mime="application/pdf",
        )


def render_comparison_page() -> None:
    """Render a side-by-side comparison for two resume PDFs."""
    st.subheader("Resume Comparison")
    col1, col2 = st.columns(2)

    with col1:
        resume_a = st.file_uploader("Upload Resume A", type=["pdf"], key="compare_a")
    with col2:
        resume_b = st.file_uploader("Upload Resume B", type=["pdf"], key="compare_b")

    if st.button("Compare Resumes"):
        if not resume_a or not resume_b:
            st.error("Please upload both resumes to compare.")
            return

        summary_a = quick_resume_summary(resume_a.getvalue())
        summary_b = quick_resume_summary(resume_b.getvalue())

        if "error" in summary_a or "error" in summary_b:
            st.error("One of the files has no extractable text. Please try another PDF.")
            return

        score_a = summary_a["score"]
        score_b = summary_b["score"]

        result_col1, result_col2 = st.columns(2)
        with result_col1:
            st.metric("Resume A Score", f"{score_a} / 100")
            st.metric("Resume A Role", summary_a["role"])
            st.caption("Top Skills")
            st.write(", ".join(skill.title() for skill in summary_a["skills"][:10]) or "No skills detected")

        with result_col2:
            st.metric("Resume B Score", f"{score_b} / 100")
            st.metric("Resume B Role", summary_b["role"])
            st.caption("Top Skills")
            st.write(", ".join(skill.title() for skill in summary_b["skills"][:10]) or "No skills detected")

        if score_a > score_b:
            st.success("Resume A currently scores higher.")
        elif score_b > score_a:
            st.success("Resume B currently scores higher.")
        else:
            st.info("Both resumes have the same score.")


def main() -> None:
    """Application entry function."""
    st.title(APP_TITLE)
    st.caption("Professional, beginner-friendly resume intelligence for internships and job preparation.")

    with st.sidebar:
        st.header("Navigation")
        page = st.radio("Go to", ["Resume Analyzer", "Resume Comparison"])
        theme = st.selectbox("Theme", ["Light", "Dark"], index=0)

    apply_theme(theme)

    if page == "Resume Analyzer":
        render_analyzer_page()
    else:
        render_comparison_page()


if __name__ == "__main__":
    main()
