# talent-agent

# AI-Powered Talent Scouting & Engagement Agent
💡 Problem Statement

**Recruiters spend significant time:**
Manually screening candidate profiles
Identifying relevant skills
Reaching out to candidates with uncertain interest

**This leads to:**
Low efficiency
Poor candidate conversion rates
Delayed hiring decisions

# Solution

This project presents an AI-powered Talent Scouting & Engagement Agent that:

Parses job descriptions using AI
Matches candidates based on skills, experience, and role alignment
Estimates candidate interest using AI reasoning
Produces a ranked shortlist with explainable insights

# System Architecture
User Input (Job Description)
        ↓
JD Parsing (LLM - Groq)
        ↓
Matching Engine (Rule-based Logic)
        ↓
Interest Estimation (LLM)
        ↓
Ranking Engine (Weighted Scoring)
        ↓
Chatbot UI (Streamlit)

 # Key Features
1. AI-Based Job Description Parsing
Extracts skills and experience dynamically using LLM
Handles unstructured recruiter inputs
2. Multi-Dimensional Candidate Scoring
Each candidate is evaluated on:
Match Score
Skill overlap
Experience alignment
Role relevance
Interest Score
AI-estimated likelihood of candidate engagement
3. Critical Skill Penalty (Real-world logic)
Missing essential skills (e.g., Django, Spring) results in score reduction
Ensures high precision in candidate selection
4. Role-Aware Matching
Differentiates between:
Data Analyst
Software Developer
Backend Engineer
Prevents irrelevant candidates from ranking high
5. Explainable AI Output

# Each recommendation includes:

Matched skills
Missing critical skills
Experience alignment
AI-generated reasoning

# This improves trust and usability for recruiters

6. Chatbot-Style Interface
Interactive UI built using Streamlit
Accepts natural language job descriptions
Displays ranked candidates conversationally

# Example Use Case
🔹 Input
Looking for Python Developer with Django and 2 years experience
🔹 Output
Kiran Patel
Match Score: 1.0
Interest Score: 0.75
Final Score: 0.92
Reason: Matched skills: Python, Django | Experience: 3 yrs

Riya Gupta
Match Score: 0.55
Reason: Missing critical skill: Django

# Tech Stack
Python
Streamlit (UI)
Groq API (LLM)
Pandas (data processing)

# Project Structure
talent-agent/
├── app.py                 # Streamlit UI
├── main.py                # Core AI + logic
├── data/
│   └── candidates.csv     # Candidate dataset
├── requirements.txt
└── README.md

# How to Run Locally
pip install -r requirements.txt
streamlit run app.py

# Live Demo

https://talent-agent-8ro7nnwx9dvwzu2i8uktbh.streamlit.app/

# Design Decisions
Used LLM only for unstructured tasks (JD parsing, interest reasoning)
Kept scoring deterministic for reliability and control
Introduced penalty-based scoring for realistic recruiter behavior

# Key Insights
Matching alone is not sufficient — interest prediction improves hiring efficiency
Explainability is critical for recruiter trust
Hybrid AI + rule-based systems are more reliable than pure AI

# Future Enhancements
Resume parsing integration
Real-time candidate sourcing (LinkedIn APIs)
Email outreach automation
Feedback-based model improvement

**Author**
Anusha H

# Conclusion

This project demonstrates how AI can:

Automate recruiter workflows
Improve candidate quality
Reduce time-to-hire

By combining AI reasoning with structured logic, the system delivers a practical and scalable hiring solution.
