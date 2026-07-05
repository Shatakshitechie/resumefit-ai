from core.extract import extract_resume_text
from core.scoring import compute_match_score
from core.analyze import analyze_resume_vs_jd


def run_full_analysis(uploaded_resume_file, jd_text: str) -> dict:
    """
    Orchestrates the full pipeline:
    1. Extract resume text from the uploaded file
    2. Compute embedding-based match score
    3. Call LLM for skill matching + suggestions
    Returns a single combined result dict, with error handling
    so partial failures don't crash the whole app.
    """
    result = {
        "success": True,
        "error": None,
        "match_score": None,
        "matched_skills": [],
        "missing_skills": [],
        "suggestions": [],
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
        llm_result = analyze_resume_vs_jd(resume_text, jd_text)
        result["matched_skills"] = llm_result.get("matched_skills", [])
        result["missing_skills"] = llm_result.get("missing_skills", [])
        result["suggestions"] = llm_result.get("suggestions", [])
    except Exception as e:
        # LLM failing shouldn't break the whole result - score can still show
        result["suggestions"] = []
        result["error"] = (result["error"] or "") + f" | LLM analysis failed: {str(e)}"

    return result