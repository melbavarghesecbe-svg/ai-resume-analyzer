"""Streamlit entry point for the AI Resume Analyzer project."""

import io

import streamlit as st

from config import APP_TITLE
from utils.insights import evaluate_target_role_strength
from utils.matcher import build_skill_gap_roadmap, match_resume_to_job
from utils.parser import extract_text_from_pdf
from utils.report import generate_pdf
from utils.role_predictor import get_role_confidence, get_role_skills, predict_role
from utils.scorer import calculate_resume_score
from utils.skill_extractor import extract_skills

st.set_page_config(page_title=APP_TITLE, layout="wide")


def _to_progress(value: float) -> float:
    """Convert percentage values to Streamlit progress range [0, 1]."""
    return min(max(value / 100, 0.0), 1.0)


def _format_skills(skills: list[str], limit: int | None = None) -> str:
    """Format skill list as title-cased comma-separated text."""
    chosen = skills[:limit] if limit is not None else skills
    return ", ".join(skill.title() for skill in chosen)


def _render_bullets(lines: list[str]) -> None:
    """Render list values as bullet-like lines in Streamlit."""
    for line in lines:
        st.write(f"- {line}")


def apply_theme(theme_name: str) -> None:
    """Apply polished light/dark styling with dashboard-like visual hierarchy."""
    if theme_name == "Dark":
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

            :root {
                --bg-main: radial-gradient(circle at 15% 15%, #16274a 0%, #0b1733 45%, #060f25 100%);
                --bg-surface-strong: rgba(21, 34, 64, 0.92);
                --bg-sidebar: linear-gradient(180deg, #0a1228 0%, #0a1730 100%);
                --border-soft: rgba(147, 197, 253, 0.18);
                --border-focus: rgba(56, 189, 248, 0.42);
                --text-main: #e6edf9;
                --text-muted: #a9b7d4;
                --accent-a: #38bdf8;
                --accent-b: #22d3ee;
            }

            .stApp {
                background: var(--bg-main);
                color: var(--text-main);
                font-family: 'Manrope', 'Segoe UI', sans-serif;
            }

            .block-container {
                padding-top: 1.5rem;
                max-width: 1180px;
            }

            h1, h2, h3, h4, h5 {
                font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
                color: var(--text-main);
            }

            p, li, label, span {
                color: var(--text-main);
            }

            section[data-testid="stSidebar"] {
                background: var(--bg-sidebar);
                border-right: 1px solid var(--border-soft);
                width: 360px;
                min-width: 360px;
            }

            section[data-testid="stSidebar"] * {
                color: var(--text-main);
            }

            .nav-title {
                font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
                font-size: 2rem;
                font-weight: 800;
                margin: 0 0 8px 0;
            }

            .nav-subtitle {
                color: var(--text-muted);
                margin: 0 0 14px 0;
                font-weight: 600;
                font-size: 1rem;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] {
                padding: 16px;
                border-radius: 16px;
                border: 1px solid var(--border-focus);
                background: linear-gradient(180deg, rgba(56, 189, 248, 0.16), rgba(56, 189, 248, 0.07));
                margin-bottom: 14px;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label,
            section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p,
            section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label span {
                font-size: 1.12rem;
                font-weight: 700;
            }

            div[data-testid="stMetric"],
            div[data-testid="stFileUploader"],
            div[data-testid="stTextArea"],
            div[data-testid="stSelectbox"],
            div[data-testid="stRadio"] {
                background: var(--bg-surface-strong);
                border: 1px solid var(--border-soft);
                border-radius: 12px;
                padding: 8px;
            }

            button[kind="primary"] {
                background: linear-gradient(120deg, var(--accent-a), var(--accent-b));
                color: #031126;
                border: none;
                border-radius: 10px;
                font-weight: 700;
            }

            .app-hero {
                background: linear-gradient(120deg, rgba(56, 189, 248, 0.18), rgba(34, 211, 238, 0.15));
                border: 1px solid var(--border-focus);
                border-radius: 18px;
                padding: 20px 24px;
                margin-bottom: 20px;
            }

            .app-hero p {
                color: var(--text-muted);
            }

            .dashboard-card, .workflow-step, .utility-card {
                background: var(--bg-surface-strong);
                border: 1px solid var(--border-soft);
                border-radius: 12px;
                padding: 16px;
            }

            .feature-row {
                margin-top: 10px;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }

            .feature-chip {
                background: rgba(56, 189, 248, 0.14);
                border: 1px solid var(--border-soft);
                border-radius: 999px;
                padding: 4px 12px;
                font-size: 0.82rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

            :root {
                --bg-main: radial-gradient(circle at 15% 15%, #f3f8ff 0%, #eef4ff 45%, #f7fbff 100%);
                --bg-surface: rgba(255, 255, 255, 0.92);
                --bg-sidebar: linear-gradient(180deg, #e9f1ff 0%, #dce8fb 100%);
                --border-soft: rgba(30, 64, 175, 0.16);
                --border-focus: rgba(14, 116, 144, 0.35);
                --text-main: #0f1f3d;
                --text-muted: #4d6187;
                --accent-a: #0ea5e9;
                --accent-b: #0891b2;
            }

            .stApp {
                background: var(--bg-main);
                color: var(--text-main);
                font-family: 'Manrope', 'Segoe UI', sans-serif;
            }

            .block-container {
                padding-top: 1.5rem;
                max-width: 1180px;
            }

            h1, h2, h3, h4, h5 {
                font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
                color: var(--text-main);
            }

            section[data-testid="stSidebar"] {
                background: var(--bg-sidebar);
                border-right: 1px solid var(--border-soft);
                width: 360px;
                min-width: 360px;
            }

            .nav-title {
                font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
                font-size: 2rem;
                font-weight: 800;
                margin: 0 0 8px 0;
            }

            .nav-subtitle {
                color: var(--text-muted);
                margin: 0 0 14px 0;
                font-weight: 600;
                font-size: 1rem;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] {
                padding: 16px;
                border-radius: 16px;
                border: 1px solid var(--border-focus);
                background: linear-gradient(180deg, rgba(14, 165, 233, 0.12), rgba(14, 165, 233, 0.05));
                margin-bottom: 14px;
            }

            section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label,
            section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p,
            section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label span {
                font-size: 1.12rem;
                font-weight: 700;
            }

            div[data-testid="stMetric"],
            div[data-testid="stFileUploader"],
            div[data-testid="stTextArea"],
            div[data-testid="stSelectbox"],
            div[data-testid="stRadio"] {
                background: var(--bg-surface);
                border: 1px solid var(--border-soft);
                border-radius: 12px;
                padding: 8px;
            }

            button[kind="primary"] {
                background: linear-gradient(120deg, var(--accent-a), var(--accent-b));
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-weight: 700;
            }

            .app-hero {
                background: linear-gradient(120deg, rgba(14, 165, 233, 0.16), rgba(8, 145, 178, 0.11));
                border: 1px solid var(--border-focus);
                border-radius: 18px;
                padding: 20px 24px;
                margin-bottom: 20px;
            }

            .app-hero p {
                color: var(--text-muted);
            }

            .dashboard-card, .workflow-step, .utility-card {
                background: var(--bg-surface);
                border: 1px solid var(--border-soft);
                border-radius: 12px;
                padding: 16px;
            }

            .feature-row {
                margin-top: 10px;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }

            .feature-chip {
                background: rgba(14, 165, 233, 0.14);
                border: 1px solid var(--border-soft);
                border-radius: 999px;
                padding: 4px 12px;
                font-size: 0.82rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


def render_hero() -> None:
    """Render app hero section."""
    st.markdown(
        f"""
        <div class="app-hero">
            <h1>{APP_TITLE}</h1>
            <p>Professional, beginner-friendly resume intelligence for internships and job preparation.</p>
            <div class="feature-row">
                <span class="feature-chip">AI Score Insights</span>
                <span class="feature-chip">Role Prediction</span>
                <span class="feature-chip">PDF Reports</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_utilities(selected_page: str) -> None:
    """Render useful sidebar context cards."""
    st.sidebar.markdown(
        f"""
        <div class="utility-card">
            <h5>Current View</h5>
            <p>You are in <strong>{selected_page}</strong>. Use this panel to move through the resume workflow.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div class="utility-card">
            <h5>Best Practice</h5>
            <p>Analyze first, improve second, compare versions third.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_page() -> None:
    """Render dashboard landing page."""
    st.subheader("Dashboard")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Modules", "3", help="Analyzer, Comparison, PDF Report")
    with c2:
        st.metric("Score Scale", "0 - 100")
    with c3:
        st.metric("Input Formats", "PDF")
    with c4:
        st.metric("Comparison Mode", "2 Resumes")

    top1, top2, top3 = st.columns(3)
    with top1:
        st.markdown(
            """
            <div class="dashboard-card">
                <h4>Resume Analyzer</h4>
                <p>Upload one resume, paste a JD, and get score, role prediction, match, and roadmap.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top2:
        st.markdown(
            """
            <div class="dashboard-card">
                <h4>Resume Comparison</h4>
                <p>Compare two resume versions side by side and pick the stronger one.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top3:
        st.markdown(
            """
            <div class="dashboard-card">
                <h4>Export Report</h4>
                <p>Download a clean PDF report with score, role, match, and recommendations.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("### Customer Workflow")
    w1, w2, w3, w4 = st.columns(4)
    with w1:
        st.markdown("<div class='workflow-step'><h5>1. Upload Resume</h5><p>Set your baseline score.</p></div>", unsafe_allow_html=True)
    with w2:
        st.markdown("<div class='workflow-step'><h5>2. Analyze Fit</h5><p>See match and missing skills.</p></div>", unsafe_allow_html=True)
    with w3:
        st.markdown("<div class='workflow-step'><h5>3. Improve Version</h5><p>Use roadmap and suggestions.</p></div>", unsafe_allow_html=True)
    with w4:
        st.markdown("<div class='workflow-step'><h5>4. Compare + Finalize</h5><p>Select your best resume version.</p></div>", unsafe_allow_html=True)


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

    insight = score_data.get("insight", "Profile has potential with targeted improvements.")

    report_payload = {
        "role": predicted_role,
        "score": score_data["score"],
        "match_percentage": job_match["match_percentage"],
        "match_level": job_match.get("match_level", "Low"),
        "skills": skills,
        "missing_skills": job_match["missing_skills"],
        "suggestions": score_data["suggestions"],
        "breakdown": score_data["breakdown"],
        "insight": insight,
    }

    return {
        "skills": skills,
        "role": predicted_role,
        "role_confidence": role_confidence,
        "job_match": job_match,
        "score": score_data,
        "insight": insight,
        "pdf_bytes": generate_pdf(report_payload),
    }


@st.cache_data(show_spinner=False)
def quick_resume_summary(file_bytes: bytes) -> dict:
    """Generate quick score/role summary for comparison."""
    resume_text = extract_text_from_pdf(io.BytesIO(file_bytes))
    if not resume_text:
        return {"error": "No extractable text found."}

    skills = extract_skills(resume_text)
    role = predict_role(skills)
    score_data = calculate_resume_score(resume_text, skills)

    return {"role": role, "score": score_data["score"], "skills": skills}


def render_breakdown(breakdown: dict) -> None:
    """Render weighted score components as progress bars."""
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
        st.progress(_to_progress(value))


def render_discovery_results(result: dict) -> None:
    """Render results for beginners exploring suitable roles."""
    st.success("Career discovery analysis completed.")

    score = result["score"]["score"]
    st.metric("Overall Resume Score", f"{score} / 100")
    st.progress(_to_progress(score))

    st.subheader("Best-Fit Roles From Your Current Resume")
    ranked_roles = sorted(result["role_confidence"].items(), key=lambda item: item[1], reverse=True)
    role_rows = [{"Role": role_name, "Fit Confidence (%)": confidence} for role_name, confidence in ranked_roles]
    st.table(role_rows)

    top_role, top_conf = ranked_roles[0]
    st.success(f"Top suggested role right now: {top_role} ({top_conf}%)")

    st.subheader("Detected Strength Signals")
    if result["skills"]:
        st.write(_format_skills(result["skills"], limit=12))
    else:
        st.warning("No clear skills were detected. Try a text-selectable PDF.")

    st.subheader("Insight")
    st.info(result["insight"])

    st.subheader("Beginner Improvement Priorities")
    _render_bullets(result["score"].get("suggestions", []))


def render_target_role_results(result: dict, target_eval: dict, jd_used: bool) -> None:
    """Render results for 4th-year users with target role focus."""
    st.success("Target role strength analysis completed.")

    score = result["score"]["score"]
    st.metric("Overall Resume Score", f"{score} / 100")
    st.progress(_to_progress(score))

    st.subheader("Target Role Strength")
    st.metric(f"{target_eval['target_role']} Strength", f"{target_eval['strength']}% ({target_eval['level']})")
    st.progress(_to_progress(target_eval["strength"]))

    col1, col2 = st.columns(2)
    with col1:
        st.write("### Matched Role Skills")
        if target_eval["matched_skills"]:
            st.success(_format_skills(target_eval["matched_skills"]))
        else:
            st.warning("No direct role-skill matches yet.")
    with col2:
        st.write("### Missing Role Skills")
        if target_eval["missing_skills"]:
            st.error(_format_skills(target_eval["missing_skills"]))
        else:
            st.success("Great coverage for this role.")

    if jd_used:
        st.subheader("Job Description Match")
        jd_match = result["job_match"]["match_percentage"]
        jd_level = result["job_match"].get("match_level", "Low")
        st.write(f"Match: {jd_match}% ({jd_level})")
        st.progress(_to_progress(jd_match))

    st.subheader("Action Plan To Improve Target Readiness")
    roadmap = build_skill_gap_roadmap(target_eval["missing_skills"])
    _render_bullets(roadmap)


def render_analyzer_page() -> None:
    """Render two analyzer workflows: Beginner and 4th-Year."""
    st.subheader("Resume Analyzer")
    beginner_tab, advanced_tab = st.tabs([
        "Career Discovery (Beginner)",
        "Target Role Strength (4th Year)",
    ])

    with beginner_tab:
        st.caption("For students exploring career direction.")
        beginner_file = st.file_uploader("Upload Resume PDF", type=["pdf"], key="discover_uploader")

        if st.button("Discover My Best Roles", type="primary"):
            if not beginner_file:
                st.error("Please upload a resume PDF before analysis.")
            else:
                with st.spinner("Analyzing your resume for role fit and quality..."):
                    result = analyze_resume_file(beginner_file.getvalue(), "")

                if "error" in result:
                    st.error(result["error"])
                else:
                    render_discovery_results(result)
                    st.subheader("Score Breakdown")
                    render_breakdown(result["score"]["breakdown"])

                    st.download_button(
                        label="Download Career Discovery Report",
                        data=result["pdf_bytes"],
                        file_name="career_discovery_report.pdf",
                        mime="application/pdf",
                    )

    with advanced_tab:
        st.caption("For final-year students who know their target field and want role-specific strength.")
        advanced_file = st.file_uploader("Upload Resume PDF", type=["pdf"], key="target_uploader")

        role_options = sorted(get_role_confidence([]).keys())
        target_role = st.selectbox("Select Your Target Role", role_options, index=0)
        job_description = st.text_area(
            "Paste Job Description (optional for stricter matching)",
            height=140,
            key="target_jd",
        )

        if st.button("Evaluate My Target Role Strength", type="primary"):
            if not advanced_file:
                st.error("Please upload a resume PDF before analysis.")
            else:
                with st.spinner("Evaluating role-specific strength..."):
                    result = analyze_resume_file(advanced_file.getvalue(), job_description)

                if "error" in result:
                    st.error(result["error"])
                else:
                    target_eval = evaluate_target_role_strength(
                        result["skills"],
                        get_role_skills(target_role),
                        target_role,
                    )
                    render_target_role_results(result, target_eval, bool(job_description.strip()))

                    st.subheader("Score Breakdown")
                    render_breakdown(result["score"]["breakdown"])

                    st.download_button(
                        label="Download Target Role Report",
                        data=result["pdf_bytes"],
                        file_name="target_role_resume_report.pdf",
                        mime="application/pdf",
                    )


def render_comparison_page() -> None:
    """Render side-by-side comparison for two resume PDFs."""
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

        left, right = st.columns(2)
        with left:
            st.metric("Resume A Score", f"{summary_a['score']} / 100")
            st.metric("Resume A Role", summary_a["role"])
            st.caption("Top Skills")
            st.write(_format_skills(summary_a["skills"], limit=10) or "No skills detected")

        with right:
            st.metric("Resume B Score", f"{summary_b['score']} / 100")
            st.metric("Resume B Role", summary_b["role"])
            st.caption("Top Skills")
            st.write(_format_skills(summary_b["skills"], limit=10) or "No skills detected")

        if summary_a["score"] > summary_b["score"]:
            st.success("Resume A currently scores higher.")
        elif summary_b["score"] > summary_a["score"]:
            st.success("Resume B currently scores higher.")
        else:
            st.info("Both resumes have the same score.")


def main() -> None:
    """Application entry function."""
    with st.sidebar:
        st.markdown("<div class='nav-title'>Navigation</div>", unsafe_allow_html=True)
        st.markdown("<div class='nav-subtitle'>Choose a page to move through your workflow</div>", unsafe_allow_html=True)
        page = st.radio("Go to", ["Dashboard", "Resume Analyzer", "Resume Comparison"])
        theme = st.selectbox("Theme", ["Light", "Dark"], index=0)

    apply_theme(theme)
    render_sidebar_utilities(page)
    render_hero()

    if page == "Dashboard":
        render_dashboard_page()
    elif page == "Resume Analyzer":
        render_analyzer_page()
    else:
        render_comparison_page()


if __name__ == "__main__":
    main()
