# 📄 Resume ↔ Job Description Matcher

An AI-powered tool that compares a resume against a job description and returns a match score, a detailed skill-gap breakdown, and specific, actionable suggestions to improve the resume — plus a clear eligibility verdict.

Built as a personal project to explore combining deterministic NLP techniques (sentence embeddings) with LLM-based reasoning in a single, reliable pipeline.

## 🔗 Live Demo

[Add your Streamlit Community Cloud link here once deployed]

## ✨ Features

- **Match Score** — computed from a blend of technical skill coverage, soft skill coverage, and semantic similarity between the resume and job description
- **Technical Skill Matching** — deterministic, text-based matching (no hallucination risk): required skills are extracted from the JD, then checked directly against the resume
- **Soft Skill Inference** — soft skills (communication, leadership, teamwork, etc.) are inferred from the resume's actual described achievements and responsibilities, not just keyword matching, and only when the JD itself calls for them
- **Actionable Suggestions** — up to 5 specific, resume-grounded suggestions that reference actual projects and experience from the uploaded resume, not generic advice
- **Eligibility Verdict** — a clear Eligible / Partially Eligible / Not Eligible call, weighted primarily on technical fit
- **Input Validation** — detects and rejects non-resume documents (e.g., certificates) and vague/incomplete job descriptions before running a full analysis
- **Graceful Failure Handling** — API timeouts, rate limits, and authentication errors are caught and shown as friendly messages instead of crashing or producing misleading results
- **Session Rate Limiting** — caps analyses per session to keep the free-tier demo usable for everyone

## 🏗️ Architecture

```
Streamlit UI (app.py)
        │
        ▼
Orchestrator (core/orchestrator.py)
        │
        ├──► extract.py       → pulls text from uploaded PDF/DOCX
        │
        ├──► scoring.py       → sentence-transformers embeddings
        │                         → semantic similarity score
        │
        ├──► tech_skills.py   → LLM extracts required technical skills from JD
        │                         → deterministic text matching against resume
        │                         (no hallucination risk on this step)
        │
        ├──► analyze.py       → LLM infers soft skills from resume context
        │                         → generates grounded suggestions
        │                         → resume/JD validity checks
        │                         → eligibility verdict
        │
        └──► Final blended score:
                65% technical skill coverage
              + 20% soft skill coverage
              + 15% embedding similarity
```

### Why this hybrid design?

Technical skills (Docker, Python, AWS, etc.) either appear in a resume or they don't — a fact-checkable, deterministic problem. Early iterations relied entirely on the LLM to judge technical skill matches and found it would occasionally hallucinate matches that weren't actually present in the resume. Splitting the pipeline so technical skills are verified with plain text matching, while soft skills (which genuinely require contextual reasoning) stay with the LLM, produces a much more trustworthy result without sacrificing the tool's ability to work across any resume/JD domain.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **LLM**: OpenRouter free-tier models (via OpenAI-compatible API)
- **File Parsing**: PyPDF2, python-docx
- **Language**: Python

## 🚀 Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/resume-jd-matcher.git
cd resume-jd-matcher
```

### 2. Create a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
Create a `.env` file in the project root:
```
OPENROUTER_API_KEY=your_key_here
```
Get a free key at [openrouter.ai](https://openrouter.ai).

### 5. Run the app
```bash
streamlit run app.py
```

## 📋 Known Limitations

- Uses a free-tier LLM (`openrouter/free`), so occasional rate limiting or slower response times (5-20+ seconds) can occur under heavy use — the app handles this gracefully with a friendly retry message rather than crashing
- Requires text-based PDF/DOCX files; scanned or image-based resumes are detected and rejected with a clear message, since no OCR step is included
- Suggestion quality can vary slightly between runs due to free-tier model routing

## 📈 Possible Future Improvements

- Interactive, multi-turn suggestion refinement (accept/edit/regenerate individual suggestions)
- Support for scanned resumes via OCR
- Swap to a paid LLM tier for more consistent latency and output quality
- Persistent history of past analyses per user

## 📄 License

MIT
