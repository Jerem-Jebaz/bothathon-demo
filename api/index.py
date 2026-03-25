import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from groq import Groq

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

PERSONALITY_PROMPTS: Dict[str, str] = {
    "chill_friend": (
        "You are the Chill friend for college students. "
        "Tone: warm, casual, friendly, low-pressure. "
        "Keep responses short and practical. Use encouragement. "
        "Responses should be 1-4 lines."
    ),
    "strict_professor": (
        "You are the Serious teacher/mentor for college students. "
        "Tone: direct, structured, no fluff. "
        "Give concise, actionable steps with accountability. "
        "Responses should be 1-2 lines."
    ),
    "savage_roast": (
        "You are the sarcastic and kinda mean friend for college students. "
        "Tone: witty, playful roast style, but classroom-safe and non-abusive. "
        "Roast behavior, not identity. End with useful advice. Keep it concise and funny. "
        "Responses should be 1-2 lines."
    ),
}

TEMPERATURES = {
    "chill_friend": 0.75,
    "strict_professor": 0.35,
    "savage_roast": 1.0,
}


def generate_response(user_input: str, mode: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing")

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": PERSONALITY_PROMPTS[mode]},
            {"role": "user", "content": user_input},
        ],
        temperature=TEMPERATURES[mode],
        max_tokens=220,
    )

    reply = (completion.choices[0].message.content or "").strip()
    if not reply:
        return "I could not generate a response. Try again."
    return reply


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    personality = payload.get("personality") or "chill_friend"

    if not message:
        return jsonify({"error": "Message is required."}), 400

    if personality not in PERSONALITY_PROMPTS:
        return jsonify({"error": "Invalid personality mode."}), 400

    try:
        reply = generate_response(message, personality)
        return jsonify({"reply": reply})
    except Exception:
        return jsonify({"error": "Assistant is temporarily unavailable. Please try again."}), 500


@app.post("/reset")
def reset():
    return jsonify({"ok": True})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})
