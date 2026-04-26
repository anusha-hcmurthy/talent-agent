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


# ---------- JD PARSER ----------
def parse_jd(jd):
    if not client:
        return ["python", "sql"], 2  # fallback

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

        return skills, experience

    except Exception as e:
        print("JD parsing error:", e)
        return ["python", "sql"], 2


# ---------- HELPER ----------
def normalize(text):
    return text.strip().lower()


# ---------- MATCHING ----------
def calculate_match(candidate, jd_skills, jd_exp):
    cand_skills = [normalize(s) for s in candidate["Skills"].split(",")]
    jd_skills = [normalize(s) for s in jd_skills]

    matched = set(cand_skills).intersection(set(jd_skills))

    skill_score = len(matched) / max(len(jd_skills), 1)
    exp_score = min(candidate["Experience"] / jd_exp, 1)

    jd_role_keywords = ["analyst", "developer", "engineer"]

    role_score = 0.6
    for word in jd_role_keywords:
        if word in candidate["Current Role"].lower():
            role_score = 1
            break

    match_score = (0.5 * skill_score) + (0.3 * exp_score) + (0.2 * role_score)

    return round(match_score, 2), skill_score, list(matched)


# ---------- AI INTEREST ----------
def ai_interest_reasoning(candidate, jd):
    if not client:
        return 0.5, "Default interest (no API key)"

    prompt = f"""
    You are a recruiter assistant.

    Given the job description and candidate profile, estimate:
    1. Interest score (0 to 1)
    2. Short reason

    Job Description:
    {jd}

    Candidate:
    Name: {candidate["Name"]}
    Role: {candidate["Current Role"]}
    Experience: {candidate["Experience"]}
    Skills: {candidate["Skills"]}

    Output format STRICTLY:
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

    jd_skills, jd_exp = parse_jd(jd)

    print("JD Skills:", jd_skills)
    print("JD Experience:", jd_exp)

    results = []

    for _, row in df.iterrows():
        match_score, skill_score, matched = calculate_match(row, jd_skills, jd_exp)
        interest_score, interest_reason = ai_interest_reasoning(row, jd)

        final_score = round((0.7 * match_score) + (0.3 * interest_score), 2)

        results.append({
            "name": row["Name"],
            "match_score": match_score,
            "interest_score": interest_score,
            "final_score": final_score,
            "reason": f"Matched skills: {', '.join(matched) if matched else 'None'} | Experience: {row['Experience']} yrs",
            "interest_reason": interest_reason
        })

    return sorted(results, key=lambda x: x["final_score"], reverse=True)
