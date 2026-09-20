"""
EduPath entry point.

Uses Streamlit's st.navigation/st.Page API to define the sidebar instead of
the old "pages/" auto-discovery folder. Titles and icons are set here in
code (as plain Python strings) rather than baked into filenames — this
avoids a real-world issue where emoji characters in filenames can get
mangled when a zip is extracted on Windows, showing up as garbled symbols
in the sidebar.
"""

import streamlit as st

st.set_page_config(page_title="EduPath - AI Learning Agent", page_icon="🧭", layout="wide")

home = st.Page("views/home.py", title="Home", icon="🧭", default=True)
resume_upload = st.Page("views/resume_upload.py", title="Resume Upload", icon="📄")
skill_gap = st.Page("views/skill_gap.py", title="Skill Gap", icon="🧩")
roadmap = st.Page("views/roadmap.py", title="Roadmap", icon="🗺️")
progress = st.Page("views/progress.py", title="Progress", icon="📈")
chat_assistant = st.Page("views/chat_assistant.py", title="Chat Assistant", icon="💬")

pg = st.navigation([home, resume_upload, skill_gap, roadmap, progress, chat_assistant])
pg.run()
