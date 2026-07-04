from core.analyze import analyze_resume_vs_jd

resume_sample = "Experienced Python developer skilled in FastAPI, Docker, and AWS deployment. Led a team of 3 engineers."

jd_sample = "Looking for a backend engineer with Python, Docker, Kubernetes, and cloud deployment experience. Strong communication and stakeholder management skills required."

result = analyze_resume_vs_jd(resume_sample, jd_sample)

print("Matched:", result.get("matched_skills"))
print("Missing:", result.get("missing_skills"))
print("Suggestions:")
for s in result.get("suggestions", []):
    print(" -", s)