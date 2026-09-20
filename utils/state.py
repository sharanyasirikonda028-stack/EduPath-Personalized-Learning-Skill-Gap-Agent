"""
Lightweight state persistence for EduPath.

Uses a single JSON file instead of a database so the whole project stays
easy to read and demo in a 2-day hackathon. Swap this out for SQLite/Postgres
later if you want to support multiple learners at once.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
STATE_FILE = os.path.join(DATA_DIR, "state.json")

DEFAULT_STATE = {
    "profile": {},
    "resume": {"skills": [], "certificates": [], "projects": []},
    "manual_skills": [],
    "gap_analysis": {},
    "roadmap": [],
    "progress": {},        # {"Week 1 - Python Revision": {"done": True, "struggled": False}, ...}
    "chat_history": [],
    "latest_report": {},
}


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_state() -> dict:
    ensure_data_dir()
    if not os.path.exists(STATE_FILE):
        return json.loads(json.dumps(DEFAULT_STATE))
    with open(STATE_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = json.loads(json.dumps(DEFAULT_STATE))
    for key, value in DEFAULT_STATE.items():
        data.setdefault(key, value)
    return data


def save_state(state: dict):
    ensure_data_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def reset_state():
    ensure_data_dir()
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
