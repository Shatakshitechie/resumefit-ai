import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openrouter/free"

def analyze_resume_vs_jd(resume_text: str, jd_text: str) -> dict:
    """
    Sends resume + JD to the LLM, asks for matched/missing skills
    and improvement suggestions, returned as structured JSON.
    """
    prompt = f"""You are a resume analysis assistant. Compare the resume below against the job description.

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Respond with ONLY a valid JSON object (no other text, no markdown formatting) in exactly this structure:
{{
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3", "skill4"],
  "suggestions": [
    "suggestion 1 - specific and actionable, under 25 words",
    "suggestion 2",
    "suggestion 3"
  ]
}}

Rules:
- matched_skills: skills/requirements from the JD that ARE present in the resume
- missing_skills: skills/requirements from the JD that are NOT present in the resume
- suggestions: 3-5 specific, actionable improvements referencing actual resume content
- Output ONLY the JSON object, nothing else
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw_output = response.choices[0].message.content.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        if raw_output.startswith("json"):
            raw_output = raw_output[4:].strip()

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        result = {
            "matched_skills": [],
            "missing_skills": [],
            "suggestions": ["Could not parse suggestions. Please try again."],
            "raw_output": raw_output
        }

    return result