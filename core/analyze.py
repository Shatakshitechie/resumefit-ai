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


def is_job_description_like(jd_text: str) -> dict:
    """
    Checks if the pasted text contains enough concrete information to be
    treated as a real job description (not just vague/casual text).
    """
    prompt = f"""Look at the following text and determine if it contains 
enough concrete, specific information to be treated as a real job description 
(e.g., mentions specific skills, technologies, responsibilities, or 
requirements) - not just vague, generic statements.

TEXT:
{jd_text[:1500]}

Respond with ONLY a valid JSON object, nothing else:
{{
  "is_valid_jd": true or false,
  "reason": "brief one-sentence explanation"
}}
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
        result = json.loads(raw_output)
        return result
    except json.JSONDecodeError:
        return {"is_valid_jd": True, "reason": "Could not verify, proceeding anyway."}


def analyze_resume_vs_jd(resume_text: str, jd_text: str, matched_technical: list, missing_technical: list) -> dict:
    """
    Handles soft skills (via inference), suggestions, and eligibility verdict.
    Technical skills are passed in already-computed (from tech_skills.py)
    so the LLM can reference them accurately without re-judging them.
    """
    prompt = f"""You are a resume analysis assistant. Compare the resume below against the job description.

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

ALREADY-CONFIRMED TECHNICAL SKILLS (verified by direct text matching, do not re-evaluate these):
- Matched: {', '.join(matched_technical) if matched_technical else 'None'}
- Missing: {', '.join(missing_technical) if missing_technical else 'None'}

Your job now is ONLY to evaluate SOFT SKILLS and provide suggestions + a verdict.

For SOFT SKILLS (communication, leadership, teamwork, stakeholder management, 
problem-solving, adaptability, etc.): Do NOT just search for literal words. 
INFER their presence from the resume's described actions, achievements, and 
responsibilities. Only mark a soft skill as missing if there is truly no 
direct or indirect evidence anywhere in the resume.

Respond with ONLY a valid JSON object (no other text, no markdown formatting) in exactly this structure:
{{
  "matched_soft_skills": ["skill1", "skill2"],
  "missing_soft_skills": ["skill3", "skill4"],
  "suggestions": [
    "suggestion 1 - specific and actionable, under 25 words",
    "suggestion 2 (add only if genuinely useful, up to 5 total)"
  ],
  "eligibility_verdict": "Eligible / Partially Eligible / Not Eligible",
  "verdict_reason": "One or two sentence explanation, referencing the confirmed technical skills above and soft skills found."
}}

Rules:
- Use the ALREADY-CONFIRMED technical skills list above when reasoning about 
  suggestions and the verdict - do not contradict it or re-decide it
- suggestions: UP TO 5 improvements. EVERY suggestion MUST explicitly name a 
  specific project, role, or detail from THIS resume (e.g., name the actual 
  project title, company, or achievement mentioned in the resume) and propose 
  a concrete rewording or addition. Generic advice with no specific resume 
  reference (e.g., "highlight leadership" or "add stakeholder engagement if 
  applicable") is NOT acceptable and must not be included. If you cannot 
  connect a suggestion to something specific and clearly present in the 
  resume, do not include that suggestion at all - a shorter list of concrete, 
  resume-specific suggestions is required over generic filler. Prioritize: 
  (1) missing technical skills that are realistic to address, (2) ways to 
  better demonstrate existing soft skills using the resume's actual project 
  names and achievements, (3) structure/quantification improvements.
- eligibility_verdict: choose exactly one of "Eligible", "Partially Eligible", 
  or "Not Eligible" based PRIMARILY on technical skills match. Soft skills 
  should only affect the verdict if the JD explicitly emphasizes them as 
  critical (e.g., a client-facing or leadership role) - do not let missing 
  soft skills alone downgrade an otherwise strong technical match.
- verdict_reason: briefly justify the verdict in 1-2 sentences
- Output ONLY the JSON object, nothing else
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        timeout=30,
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
            "matched_soft_skills": [],
            "missing_soft_skills": [],
            "suggestions": ["Could not parse suggestions. Please try again."],
            "eligibility_verdict": "Unknown",
            "verdict_reason": "Could not determine eligibility due to a parsing error.",
            "raw_output": raw_output
        }

    return result


def is_resume_like(resume_text: str) -> dict:
    """
    Quick check to see if the uploaded document actually looks like a resume/CV,
    before running the full analysis pipeline on it.
    """
    prompt = f"""Look at the following document text and determine if it is a 
resume/CV (a document describing a person's education, work experience, 
skills, and/or projects for job applications).

DOCUMENT TEXT:
{resume_text[:2000]}

Respond with ONLY a valid JSON object, nothing else:
{{
  "is_resume": true or false,
  "reason": "brief one-sentence explanation"
}}
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
        result = json.loads(raw_output)
        return result
    except json.JSONDecodeError:
        return {"is_resume": True, "reason": "Could not verify, proceeding anyway."}