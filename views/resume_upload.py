import streamlit as st
from utils.state import load_state, save_state
from utils.resume_parser import extract_text_from_pdf
from utils.llm_client import call_llm_json, is_mock_mode

if "app_state" not in st.session_state:
    st.session_state.app_state = load_state()
state = st.session_state.app_state

st.title("📄 Resume & Project Upload")

if is_mock_mode():
    st.warning("🔑 No API key set — showing placeholder demo data. Add a free Gemini key in `.env` for real AI answers.")

if not state["profile"]:
    st.warning("Please fill in your profile on the Home page first.")
    st.stop()

st.write(f"Analyzing skills for **{state['profile']['name']}**, targeting **{state['profile']['target_role']}**.")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
with col2:
    extra_text = st.text_area(
        "Or paste certificates / project descriptions / anything else relevant",
        height=150,
        placeholder=(
            "e.g. Cisco Python Essentials certificate, built a Student Performance "
            "Analyzer project using pandas and matplotlib..."
        ),
    )

if st.button("🔍 Analyze my background", type="primary"):
    combined_text = ""
    if resume_file is not None:
        with st.spinner("Reading your resume..."):
            combined_text += extract_text_from_pdf(resume_file) + "\n"
    combined_text += extra_text or ""

    if not combined_text.strip():
        st.error("Please upload a resume or paste some text first.")
    else:
        with st.spinner("EduPath is extracting your skills..."):
            system = (
                "You are a resume and project analysis agent for EduPath, a learning platform. "
                "Extract structured information from the learner's resume/text. "
                "Reply ONLY with a JSON object with keys: "
                "skills (list of strings), certificates (list of strings), projects (list of strings). "
                "Only include things explicitly supported by the text."
            )
            user = f"Learner's resume/certificates/project text:\n\n{combined_text}"
            try:
                result = call_llm_json(system, user, mock_key="resume_extract")
                state["resume"] = {
                    "skills": result.get("skills", []),
                    "certificates": result.get("certificates", []),
                    "projects": result.get("projects", []),
                }
                save_state(state)
                st.success("Extraction complete!")
            except Exception as e:
                st.error(f"Something went wrong analyzing your resume: {e}")

if state["resume"]["skills"] or state["resume"]["certificates"] or state["resume"]["projects"]:
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Detected skills**")
        st.write(", ".join(state["resume"]["skills"]) or "—")
    with c2:
        st.markdown("**Certificates found**")
        st.write(", ".join(state["resume"]["certificates"]) or "—")
    with c3:
        st.markdown("**Projects found**")
        st.write(", ".join(state["resume"]["projects"]) or "—")

    st.divider()
    st.markdown("**Anything missing?** Add extra skills manually:")
    manual = st.text_input("Comma-separated skills", value=", ".join(state.get("manual_skills", [])))
    if st.button("Save manual skills"):
        state["manual_skills"] = [s.strip() for s in manual.split(",") if s.strip()]
        save_state(state)
        st.success("Saved. Head to **🧩 Skill Gap** next.")
