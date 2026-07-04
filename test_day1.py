from core.scoring import compute_match_score

resume_sample = "Experienced Python developer skilled in FastAPI, Docker, and AWS deployment."
jd_sample = "Looking for a backend engineer with Python, Docker, and cloud deployment experience."

score = compute_match_score(resume_sample, jd_sample)
print(f"Match score: {score:.2f}")