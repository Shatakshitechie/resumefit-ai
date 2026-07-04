from sentence_transformers import SentenceTransformer, util

# Load model once when the module is imported (not on every function call)
_model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_match_score(resume_text: str, jd_text: str) -> float:
    """
    Returns a similarity score between 0 and 1 representing
    how closely the resume matches the job description.
    """
    embeddings = _model.encode([resume_text, jd_text], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    return float(similarity.item())