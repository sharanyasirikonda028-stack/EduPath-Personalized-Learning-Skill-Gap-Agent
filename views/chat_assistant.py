import streamlit as st
from utils.state import load_state, save_state
from utils.llm_client import call_llm, is_mock_mode

if "app_state" not in st.session_state:
    st.session_state.app_state = load_state()
state = st.session_state.app_state

st.title("💬 EduPath Chat Assistant")
st.caption("Ask anything about your learning journey — EduPath answers using your actual profile, roadmap, and progress.")

if is_mock_mode():
    st.warning("🔑 No API key set — showing a placeholder reply. Add a free Gemini key in `.env` for real AI answers.")

if not state["profile"]:
    st.warning("Please fill in your profile on the Home page first.")
    st.stop()

for msg in state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("e.g. What should I learn after Python? / I only have 2 hours today, plan it for me")

if question:
    state["chat_history"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    done_topics = [k for k, v in state["progress"].items() if v.get("done")]
    struggled_topics = [k for k, v in state["progress"].items() if v.get("struggled")]

    system = (
        "You are EduPath, a friendly and encouraging AI learning coach. Answer the learner's "
        "question grounded in their actual profile, roadmap, and progress data below. Be specific "
        "and actionable. Keep answers concise (a few sentences or a short list)."
    )
    context = (
        f"Learner: {state['profile']['name']}, level: {state['profile']['level']}, "
        f"target role: {state['profile']['target_role']}, daily hours: {state['profile'].get('daily_hours')}\n"
        f"Missing skills: {state.get('gap_analysis', {}).get('missing_skills', [])}\n"
        f"Roadmap: {state.get('roadmap', [])}\n"
        f"Completed topics: {done_topics}\n"
        f"Struggling with: {struggled_topics}\n"
        f"Learner's question: {question}"
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = call_llm(system, context, json_mode=False)
            except Exception as e:
                answer = f"Something went wrong: {e}"
            st.write(answer)

    state["chat_history"].append({"role": "assistant", "content": answer})
    save_state(state)
