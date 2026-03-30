import streamlit as st
from utils import analyze_resume, extract_text_from_pdf, generate_pdf_report, match_job_description

st.set_page_config(page_title="AI Career Coach", layout="centered")

top_col1, top_col2 = st.columns(2)
with top_col1:
    view_mode = st.radio(
        "View Mode",
        ["Standard view", "Compact view"],
        horizontal=True,
    )
with top_col2:
    theme_mode = st.radio(
        "Theme",
        ["Modern", "Classic"],
        horizontal=True,
    )

st.markdown(
    """
    <style>
    :root {
        --bg-soft: #f3f6fb;
        --bg-card: #ffffff;
        --ink: #0f172a;
        --ink-soft: #334155;
        --line: #dbe3ef;
        --brand-1: #0f4c81;
        --brand-2: #0ea5a4;
        --good-1: #166534;
        --good-2: #22c55e;
        --warn-1: #b45309;
        --warn-2: #f59e0b;
        --bad-1: #b91c1c;
        --bad-2: #ef4444;
    }

    .main {
        padding-top: 1rem;
        background: radial-gradient(circle at 20% 0%, #eef4ff 0%, #f9fbff 45%, #ffffff 100%);
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
    }

    .block-container {
        max-width: 980px;
        padding-top: 1.1rem;
        padding-bottom: 2.2rem;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(8px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .hero-card,
    .panel-card,
    .section-card,
    .score-box,
    .match-box,
    .missing-card {
        animation: fadeInUp 340ms ease-out;
    }

    @media (prefers-reduced-motion: reduce) {
        .hero-card,
        .panel-card,
        .section-card,
        .score-box,
        .match-box,
        .missing-card {
            animation: none;
        }
    }

    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #dbe3ef, transparent);
        margin: 1rem 0 1.1rem 0;
    }

    .hero-card {
        background: linear-gradient(120deg, var(--brand-1), var(--brand-2));
        color: #ffffff;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 24px rgba(15, 76, 129, 0.16);
    }

    .hero-title {
        margin: 0;
        font-size: 1.55rem;
        font-weight: 700;
        line-height: 1.2;
    }

    .hero-subtitle {
        margin-top: 6px;
        opacity: 0.95;
        font-size: 0.95rem;
    }

    .hero-tag {
        display: inline-block;
        margin-bottom: 8px;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.35);
    }

    .panel-card {
        background: var(--bg-card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 14px 16px;
        margin-top: 8px;
        margin-bottom: 12px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
    }

    .report-title {
        color: var(--ink);
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0 0 10px 0;
    }

    .section-title {
        color: var(--ink);
        font-size: 1.05rem;
        font-weight: 700;
        margin: 2px 0 6px 0;
    }

    .section-heading {
        color: var(--ink);
        margin-bottom: 6px;
    }

    .divider-space {
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .section-card {
        background: var(--bg-soft);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 14px 16px 12px 16px;
        margin-top: 8px;
        margin-bottom: 12px;
    }

    .section-card ul,
    .missing-card ul {
        margin-top: 0;
        margin-bottom: 0;
        padding-left: 18px;
        color: var(--ink-soft);
        line-height: 1.5;
    }

    .score-box {
        background: linear-gradient(135deg, #0f766e, #0ea5a4);
        color: white;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.28);
        padding: 18px 16px;
        text-align: center;
        margin-top: 8px;
        box-shadow: 0 8px 20px rgba(15, 118, 110, 0.2);
    }

    .score-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 4px;
    }

    .score-value {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.1;
    }

    .role-badge {
        display: inline-block;
        background: #eaf6ff;
        color: #0f4c81;
        border: 1px solid #bfdbfe;
        border-radius: 999px;
        padding: 7px 12px;
        font-weight: 600;
        margin-top: 8px;
    }

    .match-box {
        color: white;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.28);
        padding: 16px;
        text-align: center;
        margin-top: 8px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.15);
    }

    .match-low {
        background: linear-gradient(135deg, var(--bad-1), var(--bad-2));
    }

    .match-medium {
        background: linear-gradient(135deg, var(--warn-1), var(--warn-2));
    }

    .match-high {
        background: linear-gradient(135deg, var(--good-1), var(--good-2));
    }

    .missing-card {
        background: #fff1f2;
        border: 1px solid #fecdd3;
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 8px;
        margin-bottom: 8px;
    }

    div[data-testid="stFileUploader"],
    div[data-testid="stTextArea"] {
        background: #f8fbff;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 8px 10px;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: #ffffff;
    }

    .section-gap {
        margin-top: 2px;
        margin-bottom: 2px;
    }

    .stButton > button {
        width: 100%;
        border: none;
        border-radius: 10px;
        background: linear-gradient(120deg, var(--brand-1), var(--brand-2));
        color: #ffffff;
        font-weight: 700;
        padding: 0.58rem 0.8rem;
        box-shadow: 0 7px 16px rgba(15, 76, 129, 0.2);
    }

    .stDownloadButton > button {
        border-radius: 10px;
        border: 1px solid var(--line);
        background: #ffffff;
        color: var(--ink);
        font-weight: 600;
    }

    @media (max-width: 768px) {
        .hero-title {
            font-size: 1.3rem;
        }
        .score-value {
            font-size: 1.6rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if theme_mode == "Classic":
    st.markdown(
        """
        <style>
        :root {
            --bg-soft: #f6f7f9;
            --bg-card: #ffffff;
            --brand-1: #1f2937;
            --brand-2: #4b5563;
        }
        .main {
            background: radial-gradient(circle at 20% 0%, #f4f6f8 0%, #fbfcfd 45%, #ffffff 100%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        :root {
            --bg-soft: #f3f6fb;
            --bg-card: #ffffff;
            --brand-1: #0f4c81;
            --brand-2: #0ea5a4;
        }
        .main {
            background: radial-gradient(circle at 20% 0%, #eef4ff 0%, #f9fbff 45%, #ffffff 100%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

if view_mode == "Compact view":
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 940px;
            padding-top: 0.8rem;
            padding-bottom: 1.4rem;
        }
        .hero-card {
            padding: 14px 16px;
            margin-bottom: 10px;
        }
        .hero-title {
            font-size: 1.35rem;
        }
        .hero-subtitle {
            font-size: 0.88rem;
            margin-top: 4px;
        }
        .panel-card,
        .section-card,
        .missing-card {
            padding: 10px 12px;
            margin-top: 6px;
            margin-bottom: 8px;
        }
        .score-box,
        .match-box {
            padding: 12px;
            margin-top: 6px;
        }
        .section-title {
            font-size: 0.98rem;
            margin: 0 0 4px 0;
        }
        .report-title {
            font-size: 1.2rem;
            margin: 0 0 8px 0;
        }
        .score-value {
            font-size: 1.6rem;
        }
        .score-label {
            font-size: 0.82rem;
        }
        .stButton > button,
        .stDownloadButton > button {
            padding-top: 0.44rem;
            padding-bottom: 0.44rem;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-tag">CAREER TOOLS</div>
        <h1 class="hero-title">Resume Intelligence Studio</h1>
        <div class="hero-subtitle">Upload your resume, compare it with a job description, and get clear career guidance.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

st.markdown('<div class="panel-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("📂 Upload Resume (PDF)", type=["pdf"])
job_text = st.text_area("📝 Paste Job Description", placeholder="Paste the role requirements here to compare your skills...")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    st.success("✅ Resume uploaded successfully!")

    text = extract_text_from_pdf(uploaded_file)

    with st.expander("📄 View Extracted Resume"):
        st.write(text[:1000])

    st.markdown("---")

    if st.button("🚀 Analyze Resume"):
        with st.spinner("Analyzing your resume..."):
            result = analyze_resume(text)
            jd_result = match_job_description(text, job_text)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="report-title">📊 Analysis Report</h2>', unsafe_allow_html=True)
        st.markdown(" ")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<h3 class="section-title">🧠 Skills</h3>', unsafe_allow_html=True)
            skills = result.get("skills", [])
            if skills:
                skill_lines = "".join([f"<li>✅ {skill.title()}</li>" for skill in skills])
                st.markdown(
                    f"""
                    <div class="section-card">
                        <ul>{skill_lines}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<div class="section-card">No skills detected.</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<h3 class="section-title">📈 Resume Score</h3>', unsafe_allow_html=True)
            score = result.get("score", 0)
            st.markdown(
                f"""
                <div class="score-box">
                    <div class="score-label">Resume Strength</div>
                    <div class="score-value">{score} / 10</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("### 🎯 Predicted Role")
            role = result.get("role", "General Tech Role")
            st.markdown(f'<span class="role-badge">{role}</span>', unsafe_allow_html=True)

        st.markdown('<h3 class="section-title">💡 Suggestions</h3>', unsafe_allow_html=True)
        suggestions = result.get("suggestions", [])
        if suggestions:
            suggestion_lines = "".join([f"<li>{s}</li>" for s in suggestions])
            st.markdown(
                f"""
                <div class="section-card">
                    <ul>{suggestion_lines}</ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="section-card">No suggestions available.</div>', unsafe_allow_html=True)

        breakdown = result.get("breakdown", {})

        st.markdown("### 📊 Score Breakdown")

        st.progress(min(max(breakdown.get("skills", 0) / 10, 0.0), 1.0))
        st.caption("Skills")

        st.progress(min(max(breakdown.get("projects", 0) / 10, 0.0), 1.0))
        st.caption("Projects")

        st.progress(min(max(breakdown.get("experience", 0) / 10, 0.0), 1.0))
        st.caption("Experience")

        if job_text and job_text.strip():
            st.markdown("### 🧩 Job Description Match")

            match_percentage = jd_result.get("match_percentage", 0)

            if match_percentage < 40:
                match_class = "match-low"
                match_status = "Low Match"
            elif match_percentage < 70:
                match_class = "match-medium"
                match_status = "Moderate Match"
            else:
                match_class = "match-high"
                match_status = "Strong Match"

            st.markdown(
                f"""
                <div class="match-box {match_class}">
                    <div class="score-label">Match Percentage</div>
                    <div class="score-value">{match_percentage}%</div>
                    <div class="score-label">{match_status}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            compare_col1, compare_col2 = st.columns(2)

            with compare_col1:
                st.markdown("#### ✅ Matching Skills")
                matched_skills = jd_result.get("matched_skills", [])
                if matched_skills:
                    matched_lines = "".join([f"<li>{skill.title()}</li>" for skill in matched_skills])
                    st.markdown(
                        f"""
                        <div class="section-card">
                            <ul style="margin: 0; padding-left: 18px;">{matched_lines}</ul>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown('<div class="section-card">No matching skills found.</div>', unsafe_allow_html=True)

            with compare_col2:
                st.markdown("#### ⚠️ Missing Skills")
                missing_skills = jd_result.get("missing_skills", [])
                if missing_skills:
                    missing_lines = "".join([f"<li>{skill.title()}</li>" for skill in missing_skills])
                    st.markdown(
                        f"""
                        <div class="missing-card">
                            <ul>{missing_lines}</ul>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown('<div class="section-card">No missing skills. Great match!</div>', unsafe_allow_html=True)

            st.markdown("#### 🎯 Recommended Skills to Learn")
            recommended_skills = jd_result.get("recommended_skills", [])
            if recommended_skills:
                recommended_lines = "".join([f"<li>{skill.title()}</li>" for skill in recommended_skills])
                st.markdown(
                    f"""
                    <div class="section-card">
                        <ul>{recommended_lines}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<div class="section-card">No recommended skills. Your resume covers the job keywords well.</div>', unsafe_allow_html=True)

        report_payload = dict(result)
        if job_text and job_text.strip():
            report_payload["job_match"] = jd_result

        pdf_report = generate_pdf_report(report_payload)

        st.markdown("### 📥 Download Report")
        st.download_button(
            label="Download Professional Report",
            data=pdf_report,
            file_name="resume_report.pdf",
            mime="application/pdf",
        )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")