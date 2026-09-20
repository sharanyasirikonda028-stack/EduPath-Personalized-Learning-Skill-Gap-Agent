# 🧭 EduPath — Personalized Learning & Skill Gap Agent

Built for the Agentic AI Hackathon 2026 (Problem Statement 1).

EduPath is an adaptive AI agent — not a static roadmap generator. It analyzes a
learner's resume and goals, finds skill gaps against a target career, builds a
personalized weekly roadmap, and **replans that roadmap automatically** as the
learner reports progress or struggle. It also answers free-form questions
about the learner's own journey.

## Why this is "agentic" and not just a chatbot

Most one-shot tools generate a plan once and stop. EduPath's roadmap agent is
called twice: once to generate the initial plan, and again — with the
learner's completed and struggling topics fed back in — to **replan**. The
plan visibly changes based on real progress. That loop is the core of the
"adaptive learning agent" the problem statement asks for.

## Features

- **Resume analyzer** — upload a PDF resume or paste certificates/projects; an
  LLM extracts skills, certificates, and projects.
- **Skill gap analysis** — compares current skills against the target role,
  returns missing skills and a career match score.
- **Adaptive roadmap** — generates a 4–6 week plan with topics, resources,
  practice tasks, and a project idea per week. Re-running it after progress is
  logged produces an updated plan that skips what's done and reinforces what's
  weak.
- **Progress tracker** — check off completed topics, flag struggles, see
  overall completion %, and generate a weak-area report you can download.
- **Natural-language chat assistant** — ask questions like "what should I
  learn after Python?" and get answers grounded in your actual roadmap and
  progress data.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | Streamlit (multipage app) |
| AI model | Google Gemini API (`gemini-2.5-flash` by default) — **free tier, no credit card required** |
| Resume parsing | pdfplumber |
| Storage | Local JSON file (`data/state.json`) — simple and demo-friendly; swap for SQLite/Postgres for multi-user use |
| Charts | Plotly |

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Get a FREE API key (no credit card needed)
#    Go to https://aistudio.google.com/apikey, sign in with any Google account,
#    click "Create API key", and copy it.

# 3. Add your key
cp .env.example .env
# then open .env and paste your key after GEMINI_API_KEY=

# 4. Run the app
streamlit run app.py
```

The app opens in your browser. Use the sidebar to move through: Home →
Resume Upload → Skill Gap → Roadmap → Progress → Chat Assistant.

### Demo mode (no API key yet?)

If you haven't added a key yet, the app still runs completely — every page
shows a yellow "no API key set" banner and displays clearly-labeled
placeholder data instead of crashing. This lets you build and test the UI
before you have a key. **For your actual hackathon submission, add a real
key** so the AI Integration part of the judging actually reflects live AI
calls — that's 25% of your score.

If you hit Gemini's free-tier rate limit (10 requests/minute on
`gemini-2.5-flash`), switch `GEMINI_MODEL` in `.env` to `gemini-2.5-flash-lite`,
which has a higher free-tier limit.

## Folder structure

```
EduPath-AI-Agent/
├── app.py                     # Router (defines sidebar pages/icons in code)
├── requirements.txt
├── .env.example
├── utils/
│   ├── llm_client.py          # Gemini wrapper + JSON-safe parsing + demo mode
│   ├── resume_parser.py        # PDF text extraction
│   └── state.py                 # JSON-file persistence
├── views/
│   ├── home.py
│   ├── resume_upload.py
│   ├── skill_gap.py
│   ├── roadmap.py
│   ├── progress.py
│   └── chat_assistant.py
└── data/                        # state.json created here at runtime
```

> Note: page titles and icons (📄 🧩 🗺️ etc.) are set in `app.py` as plain
> Python strings, not baked into filenames. This avoids a real issue where
> emoji in filenames can get corrupted when a zip is extracted on Windows.

## Demo video script (3 minutes)

| Time | Show |
|---|---|
| 0:00–0:20 | One-line problem statement + what EduPath does |
| 0:20–0:45 | Fill in profile (name, level, target role) |
| 0:45–1:30 | Upload resume → show extracted skills → run skill gap analysis, show match score |
| 1:30–2:10 | Generate roadmap, check off a couple of topics, mark one as "struggling" |
| 2:10–2:40 | Click **Replan based on my progress** — call out that the plan changed. This is the moment that proves it's *agentic*, not a static generator |
| 2:40–3:00 | Quick chat assistant question, then close on impact / what you'd add next |

## Roadmap / next steps (mention in your pitch, don't build under time pressure)

- Multi-user auth + a real database
- PDF export of the progress report (not just .txt)
- Deeper portfolio/GitHub parsing
- Spaced-repetition style scheduling for weak topics
