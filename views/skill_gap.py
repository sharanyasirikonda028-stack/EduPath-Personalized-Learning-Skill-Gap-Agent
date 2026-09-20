import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.state import load_state, save_state
from utils.llm_client import call_llm_json, is_mock_mode

if "app_state" not in st.session_state:
    st.session_state.app_state = load_state()
state = st.session_state.app_state

st.title("🧩 Skill Gap Analysis")

if is_mock_mode():
    st.warning("🔑 No API key set — showing placeholder demo data. Add a free Gemini key in `.env` for real AI answers.")

if not state["profile"]:
    st.warning("Please fill in your profile on the Home page first.")
    st.stop()

all_known_skills = list(set(state["resume"]["skills"] + state.get("manual_skills", [])))

if st.button("🧠 Analyze my skill gap", type="primary"):
    with st.spinner("EduPath is comparing your skills to your target role..."):
        system = (
            "You are a skill-gap analysis agent for EduPath. Given a learner's current skills, "
            "experience level, and target career, identify the skills they already have that are "
            "relevant, the skills they are missing, and a career match score (0-100) representing "
            "how ready they currently are for the target role. "
            "Reply ONLY with a JSON object with keys: "
            "relevant_current_skills (list of strings), missing_skills (list of strings), "
            "match_score (integer 0-100), explanation (string, 2-3 sentences explaining the score)."
        )
        user = (
            f"Target career: {state['profile']['target_role']}\n"
            f"Experience level: {state['profile']['level']}\n"
            f"Learner's current skills: {', '.join(all_known_skills) or 'none listed'}\n"
        )
        try:
            result = call_llm_json(system, user, mock_key="skill_gap")
            state["gap_analysis"] = result
            save_state(state)
            st.success("Analysis complete!")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

if state["gap_analysis"]:
    gap = state["gap_analysis"]
    col1, col2 = st.columns([1, 2])

    with col1:
        score = gap.get("match_score", 0)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": f"Career match: {state['profile']['target_role']}"},
            gauge={"axis": {"range": [0, 100]}},
        ))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(gap.get("explanation", ""))

    with col2:
        current = gap.get("relevant_current_skills", [])
        missing = gap.get("missing_skills", [])
        max_len = max(len(current), len(missing), 1)
        current = current + [""] * (max_len - len(current))
        missing = missing + [""] * (max_len - len(missing))
        df = pd.DataFrame({"Current skills": current, "Missing skills": missing})
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.info("Ready? Head to **🗺️ Roadmap** to get your personalized weekly plan.")
