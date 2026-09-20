import streamlit as st
from utils.state import load_state, save_state
from utils.llm_client import call_llm_json, is_mock_mode

if "app_state" not in st.session_state:
    st.session_state.app_state = load_state()
state = st.session_state.app_state

st.title("🗺️ Personalized Learning Roadmap")

if is_mock_mode():
    st.warning("🔑 No API key set — showing placeholder demo data. Add a free Gemini key in `.env` for real AI answers.")

if not state.get("gap_analysis"):
    st.warning("Please run the Skill Gap analysis first.")
    st.stop()

def build_roadmap_prompt():
    completed = [k for k, v in state["progress"].items() if v.get("done")]
    struggled = [k for k, v in state["progress"].items() if v.get("struggled")]

    system = (
        "You are an adaptive learning-planner agent for EduPath. Create a week-by-week learning "
        "roadmap for the missing skills, tailored to the learner's level and daily study hours. "
        "If the learner has already completed some topics, do NOT repeat them - build on top of them. "
        "If the learner is struggling with certain topics, add extra reinforcement practice for those "
        "before moving on. "
        'Reply ONLY with a JSON object: {"weeks": [{"week": 1, "title": "...", '
        '"topics": ["..."], "resources": ["..."], "practice_tasks": ["..."], '
        '"project_idea": "..."}]}. Keep it to 4-6 weeks.'
    )
    user = (
        f"Target career: {state['profile']['target_role']}\n"
        f"Level: {state['profile']['level']}\n"
        f"Daily study hours: {state['profile'].get('daily_hours', 2)}\n"
        f"Missing skills: {', '.join(state['gap_analysis'].get('missing_skills', []))}\n"
        f"Already completed topics: {', '.join(completed) or 'none yet'}\n"
        f"Struggling with: {', '.join(struggled) or 'none reported'}\n"
    )
    return system, user

def generate_roadmap():
    system, user = build_roadmap_prompt()
    result = call_llm_json(system, user, mock_key="roadmap")
    state["roadmap"] = result.get("weeks", [])
    save_state(state)

col_a, col_b = st.columns(2)
with col_a:
    if st.button("🗓️ Generate my roadmap", type="primary", use_container_width=True):
        with st.spinner("EduPath is building your personalized roadmap..."):
            try:
                generate_roadmap()
                st.success("Roadmap generated!")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

with col_b:
    if st.button("🔁 Replan based on my progress", use_container_width=True, disabled=not state["roadmap"]):
        with st.spinner("EduPath is replanning based on what you've done so far..."):
            try:
                generate_roadmap()
                st.success("Roadmap updated based on your progress — see what changed below!")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

st.divider()

if state["roadmap"]:
    for week in state["roadmap"]:
        with st.expander(f"Week {week.get('week')}: {week.get('title', '')}", expanded=False):
            st.markdown("**Topics**")
            for topic in week.get("topics", []):
                key = f"Week {week.get('week')} - {topic}"
                cols = st.columns([3, 1, 1])
                cols[0].write(f"• {topic}")
                done = cols[1].checkbox(
                    "Done", value=state["progress"].get(key, {}).get("done", False), key=f"done_{key}"
                )
                struggled = cols[2].checkbox(
                    "Struggling", value=state["progress"].get(key, {}).get("struggled", False), key=f"struggle_{key}"
                )
                state["progress"][key] = {"done": done, "struggled": struggled}

            st.markdown("**Resources**")
            for r in week.get("resources", []):
                st.write(f"- {r}")

            st.markdown("**Practice tasks**")
            for t in week.get("practice_tasks", []):
                st.write(f"- {t}")

            if week.get("project_idea"):
                st.markdown(f"**Project idea:** {week['project_idea']}")

    save_state(state)
    st.info("Check off topics above, then click **🔁 Replan based on my progress** to see EduPath adapt your plan.")
else:
    st.info("Click **Generate my roadmap** to get started.")
