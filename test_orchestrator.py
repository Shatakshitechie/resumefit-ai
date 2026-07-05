from core.orchestrator import run_full_analysis

class FakeUploadedFile:
    """Simulates a Streamlit uploaded file for testing purposes."""
    def __init__(self, path):
        self.name = path
        self._file = open(path, "rb")

    def read(self, *args, **kwargs):
        return self._file.read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self._file.seek(*args, **kwargs)

    def tell(self, *args, **kwargs):
        return self._file.tell(*args, **kwargs)

# Update this path to match your actual resume file name
fake_file = FakeUploadedFile("Resume.pdf")

jd_text = """
Looking for a backend engineer with Python, Docker, Kubernetes, and cloud deployment experience.
Strong communication and stakeholder management skills required.
"""

result = run_full_analysis(fake_file, jd_text)

print("Success:", result["success"])
print("Error:", result["error"])
print("Match Score:", result["match_score"])
print("Matched Skills:", result["matched_skills"])
print("Missing Skills:", result["missing_skills"])
print("Suggestions:", result["suggestions"])