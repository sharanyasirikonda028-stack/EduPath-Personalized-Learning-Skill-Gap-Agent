import streamlit as st
from utils.state import load_state, save_state

if "app_state" not in st.session_state:
    st.session_state.app_state = load_state()

state = st.session_state.app_state

st.title("🧭 EduPath — Personalized Learning & Skill Gap Agent")
st.caption("An adaptive AI agent that builds you a learning roadmap, tracks your progress, and replans as you go.")

st.divider()

with st.form("welcome_form"):
    st.subheader("Tell EduPath about yourself")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your name", value=state["profile"].get("name", ""))
        level_options = ["Beginner", "Intermediate", "Advanced"]
        level = st.selectbox(
            "Experience level",
            level_options,
            index=level_options.index(state["profile"].get("level", "Beginner")),
        )
    with col2:
        role_options = ["Data Analyst", "AI Engineer", "Full Stack Developer", "Software Developer", "Other"]
        target_role = st.selectbox("Target career", role_options, index=0)
        custom_role = ""
        if target_role == "Other":
            custom_role = st.text_input("Enter your target career")
        daily_hours = st.slider("Hours you can study per day", 1, 6, state["profile"].get("daily_hours", 2))

    submitted = st.form_submit_button("Generate My Learning Path →", use_container_width=True)

if submitted:
    final_role = custom_role.strip() if target_role == "Other" and custom_role.strip() else target_role
    if not name.strip() or not final_role:
        st.error("Please enter your name and target career.")
    else:
        state["profile"] = {
            "name": name.strip(),
            "level": level,
            "target_role": final_role,
            "daily_hours": daily_hours,
        }
        save_state(state)
        st.success(f"Profile saved, {name}! Head to **Resume Upload** in the sidebar to continue.")

st.divider()
st.markdown(
    """
### How EduPath works
1. **Resume Upload** — upload your resume/certificates, and EduPath extracts your current skills.
2. **Skill Gap** — EduPath compares your skills against your target role and finds the gaps.
3. **Roadmap** — get a personalized weekly learning plan with resources and practice tasks.
4. **Progress** — mark what you've completed; EduPath **replans your roadmap automatically**.
5. **Chat Assistant** — ask EduPath anything about your learning journey, in plain language.
"""
)

if state["profile"]:
    st.info(
        f"Current profile: **{state['profile']['name']}** · {state['profile']['level']} "
        f"· aiming for **{state['profile']['target_role']}**"
    )
