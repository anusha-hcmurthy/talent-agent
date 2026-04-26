import streamlit as st
from main import run_agent

st.title("🤖 AI Talent Scouting Agent")

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
jd = st.chat_input("Enter Job Description")

# ONLY run when input is given
if jd:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": jd})
    with st.chat_message("user"):
        st.write(jd)

    # Run agent
    results = run_agent(jd)

    # Build response
    response = "### 🎯 Top 3 Candidates:\n\n"

    for r in results[:3]:
        response += f"""
**{r['name']}**
- Match Score: {r['match_score']}
- Interest Score: {r['interest_score']}
- Final Score: {r['final_score']}

📊 Fit Reason:
{r['reason']}

💬 Interest Insight:
{r['interest_reason']}

---
"""

    # Show bot response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
