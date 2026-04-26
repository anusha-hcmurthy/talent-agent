import pandas as pd
import re
import os
from groq import Groq

# ---------- GROQ SETUP ----------
api_key = os.getenv("GROQ_API_KEY")

if api_key:
    client = Groq(api_key=api_key)
else:
    client = None
    print("WARNING: GROQ API KEY NOT FOUND - using fallback")

# ---------- HELPER ----------
def normalize(text):
    return text.strip().lower()

def infer_role_from_jd(jd_text):
    jd_text = jd_text.lower()
    if "developer" in jd_text or "backend" in jd_text:
        return "developer"
    if "analyst" in jd_text:
        return "analyst"
    if "engineer" in jd_text:
        return "engineer"
    return "general"

# ---------- JD PARSER ----------
def parse_jd(jd):
    # Fallback if no API
    if not client:
        return ["python", "sql"], 2, infer_role_from_jd(jd)

    prompt = f"""
    Extract skills and years of experience from the job description.

    Return in this format:
    Skills: skill1, skill2, skill3
    Experience: number

    JD:
    {jd}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content.lower()

        skills = []
        if "skills:" in text:
            skills_part = text.split("skills:")[1].split("\n")[0]
            skills_part = re.sub(r"\d+\.\s*", "", skills_part)
            skills = [s.strip() for s in skills_part.split(",") if s.strip()]

        experience = 1
        if "experience:" in text:
            exp_part = text.split("experience:")[1]
            digits = ''.join(filter(str.isdigit, exp_part))
            if digits:
                experience = int(digits)

        role_hint = infer_role_from_jd(jd)

        return skills, experience, role_hint

    except Exception as e:
        print("JD parsing error:", e)
        return ["python", "sql"], 2, infer_role_from_jd(jd)

# ---------- MATCHING ----------
def calculate_match(candidate, jd_skills, jd_exp, role_hint):
    cand_skills = [normalize(s) for s in candidate["Skills"].split(",")]
    jd_skills = [normalize(s) for s in jd_skills]

    matched = set(cand_skills).intersection(set(jd_skills))

    # ----- CRITICAL SKILLS -----
    critical_skills = ["django", "spring", "react"]
    missing_critical = [s for s in jd_skills if s in critical_skills and s not in cand_skills]

    skill_score = len(matched) / max(len(jd_skills), 1)

    if missing_critical:
        skill_score *= 0.6  # penalty

    # ----- EXPERIENCE -----
    if candidate["Experience"] >= jd_exp:
        exp_score = 1
    else:
        exp_score = candidate["Experience"] / jd_exp

    # ----- ROLE MATCH -----
    role = candidate["Current Role"].lower()

    if role_hint == "developer":
        role_score = 1 if "developer" in role else 0.4
    elif role_hint == "analyst":
        role_score = 1 if "analyst" in role else 0.4
    elif role_hint == "engineer":
        role_score = 1 if "engineer" in role else 0.4
    else:
        role_score = 0.6

    match_score = (0.5 * skill_score) + (0.3 * exp_score) + (0.2 * role_score)

    return round(match_score, 2), skill_score, list(matched), missing_critical

# ---------- AI INTEREST ----------
def ai_interest_reasoning(candidate, jd):
    if not client:
        return 0.5, "Default interest (no API key)"

    prompt = f"""
    You are a recruiter assistant.

    STRICT RULES:
    - Do NOT hallucinate experience differences
    - If candidate meets or exceeds experience → say "meets requirement"
    - If missing a key skill (like Django), mention it clearly

    Evaluate:
    1. Interest score (0 to 1)
    2. Short realistic recruiter-style reason

    Job Description:
    {jd}

    Candidate:
    Name: {candidate["Name"]}
    Role: {candidate["Current Role"]}
    Experience: {candidate["Experience"]}
    Skills: {candidate["Skills"]}

    Output format:
    Score: 0.75
    Reason: short explanation
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content.lower()

        score = 0.5
        match = re.search(r"score:\s*(\d*\.?\d+)", text)
        if match:
            score = float(match.group(1))

        reason = "Moderate interest"
        if "reason:" in text:
            reason = text.split("reason:")[1].strip()

        return round(min(score, 1), 2), reason

    except Exception as e:
        print("Interest AI error:", e)
        return 0.5, "Fallback interest"

# ---------- MAIN AGENT ----------
def run_agent(jd):
    df = pd.read_csv("data/candidates.csv")

    jd_skills, jd_exp, role_hint = parse_jd(jd)

    print("JD Skills:", jd_skills)
    print("JD Experience:", jd_exp)
    print("Role Hint:", role_hint)

    results = []

    for _, row in df.iterrows():
        match_score, skill_score, matched, missing_critical = calculate_match(
            row, jd_skills, jd_exp, role_hint
        )

        interest_score, interest_reason = ai_interest_reasoning(row, jd)

        final_score = round((0.7 * match_score) + (0.3 * interest_score), 2)

        reason = f"Matched skills: {', '.join(matched) if matched else 'None'}"
        if missing_critical:
            reason += f" | Missing critical: {', '.join(missing_critical)}"

        reason += f" | Experience: {row['Experience']} yrs"

        results.append({
            "name": row["Name"],
            "match_score": match_score,
            "interest_score": interest_score,
            "final_score": final_score,
            "reason": reason,
            "interest_reason": interest_reason
        })

    return sorted(results, key=lambda x: x["final_score"], reverse=True)
