"""
LLM wrapper for EduPath, backed by Google's Gemini API (free tier — no
credit card required). Every page calls call_llm() / call_llm_json() so
the rest of the app never needs to know which provider is behind it.

DEMO MODE: if no GEMINI_API_KEY is set, this module automatically falls
back to placeholder mock responses so the app still runs end-to-end for
UI testing. Add a real key to .env to get live AI answers.
"""

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

_client = None
_configured = False
MOCK_MODE = False


def _setup():
    global _configured, MOCK_MODE, _client
    if _configured:
        return
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key.lower() in ("your_free_api_key_here", "your_api_key_here", ""):
        MOCK_MODE = True
    else:
        _client = genai.Client(api_key=api_key)
    _configured = True


def is_mock_mode() -> bool:
    _setup()
    return MOCK_MODE


def call_llm(system_prompt: str, user_prompt: str, json_mode: bool = True, mock_key: str = "generic") -> str:
    """Calls Gemini with a system + user prompt. Returns raw text.
    Falls back to placeholder mock data if no API key is configured."""
    _setup()
    if MOCK_MODE:
        return _mock_response(mock_key, json_mode)

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json" if json_mode else "text/plain",
        temperature=0.4,
    )
    try:
        response = _client.models.generate_content(
            model=MODEL_NAME,
            contents=user_prompt,
            config=config,
        )
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(
            f"Gemini API call failed: {e}. Check that GEMINI_API_KEY in .env is valid "
            f"and that GEMINI_MODEL ({MODEL_NAME}) is available on the free tier."
        )


def call_llm_json(system_prompt: str, user_prompt: str, mock_key: str = "generic") -> dict:
    """Calls Gemini and safely parses a JSON response, even if the model
    wraps it in markdown code fences."""
    raw = call_llm(system_prompt, user_prompt, json_mode=True, mock_key=mock_key)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            return json.loads(cleaned[start:end + 1])
        raise


# ---------------------------------------------------------------------------
# Demo-mode placeholder data (used only when no API key is set)
# ---------------------------------------------------------------------------

MOCK_LIBRARY = {
    "resume_extract": {
        "skills": ["Python", "SQL", "HTML", "CSS", "Excel"],
        "certificates": ["Sample Certificate — this is placeholder demo data"],
        "projects": ["Sample Project — add a free Gemini API key for real extraction"],
    },
    "skill_gap": {
        "relevant_current_skills": ["Python", "SQL"],
        "missing_skills": ["Power BI", "Tableau", "Statistics", "Data Visualization"],
        "match_score": 55,
        "explanation": (
            "This is placeholder demo data because no API key is set yet. "
            "Add a free Gemini API key to .env to get a real, personalized analysis."
        ),
    },
    "roadmap": {
        "weeks": [
            {
                "week": 1,
                "title": "Foundations (demo data)",
                "topics": ["Sample topic A", "Sample topic B"],
                "resources": ["Add a real API key to get real, personalized resource links"],
                "practice_tasks": ["Sample practice task"],
                "project_idea": "Sample mini project",
            },
            {
                "week": 2,
                "title": "Applied practice (demo data)",
                "topics": ["Sample topic C", "Sample topic D"],
                "resources": ["Add a real API key to unlock live recommendations"],
                "practice_tasks": ["Sample practice task"],
                "project_idea": "Sample mini project",
            },
        ]
    },
    "weak_report": {
        "strong_skills": ["Python"],
        "needs_improvement": ["Statistics"],
        "weak_area_advice": "This is placeholder text — add a real API key for a live, personalized report.",
        "next_recommendation": "Add your free Gemini API key in .env to unlock real AI answers.",
    },
    "generic": "This is a placeholder answer because no API key is configured yet. Add a free Gemini API key to .env to get real AI responses.",
}


def _mock_response(mock_key: str, json_mode: bool) -> str:
    data = MOCK_LIBRARY.get(mock_key, MOCK_LIBRARY["generic"])
    if json_mode:
        payload = data if isinstance(data, dict) else {"message": data}
        return json.dumps(payload)
    return data if isinstance(data, str) else json.dumps(data)
