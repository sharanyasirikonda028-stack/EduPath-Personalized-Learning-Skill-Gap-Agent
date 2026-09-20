import streamlit as st
import plotly.graph_objects as go
from utils.state import load_state, save_state
from utils.llm_client import call_llm_json, is_mock_mode

if "app_state" not in st.session_state:
    st.session_state.app_state = load_state()
state = st.session_state.app_state

st.title("📈 Progress Tracker")

if is_mock_mode():
    st.warning("🔑 No API key set — showing placeholder demo data. Add a free Gemini key in `.env` for real AI answers.")

if not state["roadmap"]:
    st.warning("Generate a roadmap first.")
    st.stop()

all_topics = list(state["progress"].keys())
done_topics = [k for k, v in state["progress"].items() if v.get("done")]
struggled_topics = [k for k, v in state["progress"].items() if v.get("struggled")]
remaining = [t for t in all_topics if t not in done_topics]

total = len(all_topics) or 1
pct = round(100 * len(done_topics) / total)

def short(label: str) -> str:
    return label.split(" - ", 1)[-1] if " - " in label else label

col1, col2 = st.columns([1, 2])
with col1:
    fig = go.Figure(go.Indicator(mode="gauge+number", value=pct, title={"text": "Overall progress"}))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**✅ Skills / topics completed**")
    st.write(", ".join(short(t) for t in done_topics) or "—")
    st.markdown("**⚠️ Currently struggling with**")
    st.write(", ".join(short(t) for t in struggled_topics) or "—")
    st.markdown("**⏳ Remaining topics**")
    st.write(", ".join(short(t) for t in remaining) or "—")

st.divider()

if st.button("🩺 Generate weak-area report", type="primary"):
    with st.spinner("EduPath is analyzing where you need reinforcement..."):
        system = (
            "You are a learning-diagnostics agent. Based on the learner's completed topics and "
            "the topics they marked as struggling with, write a short, encouraging report. "
            'Reply ONLY with JSON: {"strong_skills": ["..."], "needs_improvement": ["..."], '
            '"weak_area_advice": "...", "next_recommendation": "..."}'
        )
        user = (
            f"Completed topics: {', '.join(done_topics) or 'none'}\n"
            f"Struggling topics: {', '.join(struggled_topics) or 'none'}\n"
            f"Target role: {state['profile']['target_role']}\n"
        )
        try:
            report = call_llm_json(system, user, mock_key="weak_report")
            state["latest_report"] = report
            save_state(state)
        except Exception as e:
            st.error(f"Something went wrong: {e}")

if state.get("latest_report"):
    report = state["latest_report"]
    st.markdown(f"**Strong skills:** {', '.join(report.get('strong_skills', [])) or '—'}")
    st.markdown(f"**Needs improvement:** {', '.join(report.get('needs_improvement', [])) or '—'}")
    st.info(report.get("weak_area_advice", ""))
    st.success(f"Next up: {report.get('next_recommendation', '')}")

    report_text = (
        f"EduPath Progress Report for {state['profile']['name']}\n"
        f"Target role: {state['profile']['target_role']}\n"
        f"Overall progress: {pct}%\n\n"
        f"Completed: {', '.join(short(t) for t in done_topics)}\n"
        f"In progress / struggling: {', '.join(short(t) for t in struggled_topics)}\n"
        f"Remaining: {', '.join(short(t) for t in remaining)}\n\n"
        f"Strong skills: {', '.join(report.get('strong_skills', []))}\n"
        f"Needs improvement: {', '.join(report.get('needs_improvement', []))}\n"
        f"Advice: {report.get('weak_area_advice', '')}\n"
        f"Next recommendation: {report.get('next_recommendation', '')}\n"
    )
    st.download_button("⬇️ Download progress report (.txt)", report_text, file_name="edupath_progress_report.txt")
