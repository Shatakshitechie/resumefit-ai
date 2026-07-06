import streamlit as st
from core.orchestrator import run_full_analysis

st.set_page_config(
    page_title="Resume ↔ JD Matcher",
    page_icon="📄",
    layout="centered",
)

st.title("📄 Resume ↔ Job Description Matcher")
st.markdown(
    "Upload your resume and paste a job description to get a match score, "
    "skill-gap analysis, and AI-powered improvement suggestions."
)

st.divider()

# --- Rate limiting setup ---
MAX_ANALYSES_PER_SESSION = 2

if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# --- Input section ---
col1, col2 = st.columns(2)

with col1:
    uploaded_resume = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"],
        help="PDF or DOCX only. Must be a text-based file (not a scanned image or photo) so the text can be read.",
    )
    st.caption("📌 Tip: If your resume is a scanned copy or photo, please use a text-based PDF/DOCX export instead.")

with col2:
    jd_text = st.text_area(
        "Paste the job description",
        height=200,
        placeholder="Paste the full job description here...",
    )

analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

remaining = MAX_ANALYSES_PER_SESSION - st.session_state.analysis_count
st.caption(f"🔎 {remaining} analysis{'es' if remaining != 1 else ''} remaining this session")

st.divider()

# --- Handle button click: run analysis and store result ---
if analyze_clicked:
    if st.session_state.analysis_count >= MAX_ANALYSES_PER_SESSION:
        st.error(
            f"You've reached the limit of {MAX_ANALYSES_PER_SESSION} analyses for this session. "
            "Please refresh the page to reset (this limit exists to keep the free demo available for everyone)."
        )
    elif not uploaded_resume:
        st.warning("Please upload a resume first.")
    elif not jd_text or len(jd_text.strip()) < 20:
        st.warning("Please paste a complete job description.")
    else:
        with st.spinner("Analyzing... this may take a few seconds"):
            result = run_full_analysis(uploaded_resume, jd_text)
        st.session_state.analysis_count += 1
        st.session_state.last_result = result
        st.rerun()

# --- Results section: always render from stored result, not just on click ---
result = st.session_state.last_result

if result is not None:
    if not result["success"]:
        st.error(result["error"])
    else:
        # Match score
        score_pct = round(result["match_score"] * 100, 1) if result["match_score"] is not None else None

        if score_pct is not None:
            st.subheader("Match Score")
            st.metric(label="Overall Match", value=f"{score_pct}%")
            st.progress(min(int(score_pct), 100))
        else:
            st.info("Match score unavailable.")

        # Show a prominent warning if the AI analysis portion failed entirely
        if result["error"] and not result["matched_technical_skills"] and not result["missing_technical_skills"] and not result["suggestions"]:
            st.warning(f"⚠️ {result['error']}")

        st.divider()

        # Skills breakdown
        st.subheader("Skills Breakdown")

        st.markdown("#### 🛠️ Technical Skills")
        if result.get("extraction_failed"):
            st.caption("⚠️ Skill extraction had trouble this run — try clicking Analyze again for a more complete result.")
        tech_col1, tech_col2 = st.columns(2)
        with tech_col1:
            st.markdown("**✅ Matched**")
            if result["matched_technical_skills"]:
                for skill in result["matched_technical_skills"]:
                    st.markdown(f"- {skill}")
            else:
                st.markdown("_None detected_")
        with tech_col2:
            st.markdown("**❌ Missing**")
            if result["missing_technical_skills"]:
                for skill in result["missing_technical_skills"]:
                    st.markdown(f"- {skill}")
            else:
                st.markdown("_None detected_")

        st.markdown("#### 🤝 Soft Skills")
        soft_col1, soft_col2 = st.columns(2)
        with soft_col1:
            st.markdown("**✅ Matched (inferred from experience)**")
            if result["matched_soft_skills"]:
                for skill in result["matched_soft_skills"]:
                    st.markdown(f"- {skill}")
            else:
                st.markdown("_None detected_")
        with soft_col2:
            st.markdown("**❌ Missing**")
            if result["missing_soft_skills"]:
                for skill in result["missing_soft_skills"]:
                    st.markdown(f"- {skill}")
            else:
                st.markdown("_None detected_")

        st.divider()

        # Suggestions
        st.subheader("💡 Suggestions to Improve Your Resume")
        if result["suggestions"]:
            for i, suggestion in enumerate(result["suggestions"], 1):
                st.markdown(f"{i}. {suggestion}")
        else:
            st.info("No suggestions available.")

        # Eligibility verdict
        verdict = result.get("eligibility_verdict")
        reason = result.get("verdict_reason", "")

        if verdict == "Eligible":
            st.success(f"✅ **Eligible** — {reason}")
        elif verdict == "Partially Eligible":
            st.warning(f"⚠️ **Partially Eligible** — {reason}")
        elif verdict == "Not Eligible":
            st.error(f"❌ **Not Eligible** — {reason}")
        else:
            st.info("Eligibility verdict unavailable.")

st.divider()
st.caption("Built with sentence-transformers for scoring and an LLM for skill-gap analysis and suggestions.")