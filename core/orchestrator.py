from core.extract import extract_resume_text
from core.scoring import compute_match_score
from core.analyze import analyze_resume_vs_jd
from core.tech_skills import analyze_technical_skills


def compute_final_score(matched_technical, missing_technical, matched_soft, missing_soft, embedding_score):
    """
    Computes a final match score based primarily on actual skill coverage,
    with embedding similarity as a minor secondary signal.
    """
    total_technical = len(matched_technical) + len(missing_technical)
    total_soft = len(matched_soft) + len(missing_soft)

    technical_score = (len(matched_technical) / total_technical) if total_technical > 0 else 1.0
    soft_score = (len(matched_soft) / total_soft) if total_soft > 0 else 1.0

    embedding_component = embedding_score if embedding_score is not None else 0.5

    # Weighted: technical skills matter most, soft skills next, embedding least
    final_score = (0.65 * technical_score) + (0.20 * soft_score) + (0.15 * embedding_component)

    return round(final_score, 4)

def run_full_analysis(uploaded_resume_file, jd_text: str) -> dict:
    """
    Orchestrates the full pipeline:
    1. Extract resume text from the uploaded file
    2. Compute embedding-based match score
    3. Call LLM for skill matching + suggestions
    Returns a single combined result dict, with error handling so partial failures don't crash the whole app.
    """

    result = {
        "success": True,
        "error": None,
        "match_score": None,
        "matched_technical_skills": [],
        "missing_technical_skills": [],
        "matched_soft_skills": [],
        "missing_soft_skills": [],
        "suggestions": [],
        "eligibility_verdict": None,
        "verdict_reason": None,
    }

    # Step 1: Extract resume text
    try:
        resume_text = extract_resume_text(uploaded_resume_file)
        if not resume_text or len(resume_text.strip()) < 20:
            result["success"] = False
            result["error"] = "Couldn't extract readable text from the resume. Try a different file (avoid scanned/image-based PDFs)."
            return result
    except Exception as e:
        result["success"] = False
        result["error"] = f"Failed to read resume file: {str(e)}"
        return result

    # Step 2: Validate JD text
    if not jd_text or len(jd_text.strip()) < 20:
        result["success"] = False
        result["error"] = "Job description is too short or empty. Please paste a full JD."
        return result

    # Step 3: Compute match score (embeddings) - independent of LLM
    try:
        result["match_score"] = compute_match_score(resume_text, jd_text)
    except Exception as e:
        result["error"] = f"Scoring failed: {str(e)}"
        result["match_score"] = None

    # Step 4: Call LLM for skills + suggestions
    try:
        # Step A: deterministic technical skill matching
        tech_result = analyze_technical_skills(resume_text, jd_text)
        result["matched_technical_skills"] = tech_result.get("matched_technical_skills", [])
        result["missing_technical_skills"] = tech_result.get("missing_technical_skills", [])

        # Step B: LLM for soft skills, suggestions, verdict (given confirmed tech skills)
        llm_result = analyze_resume_vs_jd(
            resume_text,
            jd_text,
            result["matched_technical_skills"],
            result["missing_technical_skills"],
        )
        result["matched_soft_skills"] = llm_result.get("matched_soft_skills", [])
        result["missing_soft_skills"] = llm_result.get("missing_soft_skills", [])
        result["suggestions"] = llm_result.get("suggestions", [])
        result["eligibility_verdict"] = llm_result.get("eligibility_verdict", "Unknown")
        result["verdict_reason"] = llm_result.get("verdict_reason", "")
    except Exception as e:
        result["suggestions"] = []
        result["error"] = (result["error"] or "") + f" | Analysis failed: {str(e)}"

    # Step 5: Recalculate final score based on actual skill coverage, not just embeddings
    result["match_score"] = compute_final_score(
        result["matched_technical_skills"],
        result["missing_technical_skills"],
        result["matched_soft_skills"],
        result["missing_soft_skills"],
        result["match_score"],
    )

    return result