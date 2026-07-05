import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "openrouter/free"


def extract_technical_skills_from_jd(jd_text: str) -> list:
    """
    Asks the LLM to extract ONLY the technical skills/tools/technologies
    mentioned or implied in the JD. This is a simple extraction task
    (not a matching/judgment task), so hallucination risk is much lower.
    """
    prompt = f"""Extract a list of technical skills, tools, technologies, 
platforms, and programming languages mentioned or clearly implied in this 
job description. Do NOT include soft skills (like communication, teamwork, 
leadership).

JOB DESCRIPTION:
{jd_text}

Respond with ONLY a valid JSON array of strings, nothing else. Example format:
["Python", "Docker", "AWS", "PyTorch"]
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        timeout=30,
    )

    raw_output = response.choices[0].message.content.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        if raw_output.startswith("json"):
            raw_output = raw_output[4:].strip()

    try:
        skills = json.loads(raw_output)
        if isinstance(skills, list):
            return [str(s).strip() for s in skills if s]
    except json.JSONDecodeError:
        pass

    return []


def match_skills_in_resume(skills: list, resume_text: str) -> dict:
    """
    Deterministically checks which extracted skills actually appear
    in the resume text. Pure string matching - no LLM involved,
    so no hallucination risk here.
    """
    resume_lower = resume_text.lower()
    matched = []
    missing = []

    for skill in skills:
        skill_lower = skill.lower().strip()
        if not skill_lower:
            continue
        # Word-boundary-aware match so "java" doesn't match inside "javascript"
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, resume_lower):
            matched.append(skill)
        else:
            missing.append(skill)

    return {
        "matched_technical_skills": matched,
        "missing_technical_skills": missing,
    }


def analyze_technical_skills(resume_text: str, jd_text: str) -> dict:
    required_skills = extract_technical_skills_from_jd(jd_text)
    if not required_skills:
        return {
            "matched_technical_skills": [],
            "missing_technical_skills": [],
            "extraction_failed": True,
        }
    result = match_skills_in_resume(required_skills, resume_text)
    result["extraction_failed"] = False
    return result