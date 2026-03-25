import os
import time
from typing import Dict

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

MODE_CONFIG = {
    "Chill 😌": {"icon": "😌", "label": "Chill Mode"},
    "Get Serious 🎯": {"icon": "🎯", "label": "Serious Mode"},
    "Roast Me 💀": {"icon": "💀", "label": "Roast Mode"},
}

PERSONALITY_PROMPTS: Dict[str, str] = {
    "Chill 😌": (
        "You are Chill 😌 for first-year students. "
        "Tone: warm, casual, friendly, low-pressure. "
        "Keep responses short and practical. Use encouragement."
    ),
    "Get Serious 🎯": (
        "You are Get Serious 🎯 for first-year students. "
        "Tone: direct, structured, no fluff. "
        "Give concise, actionable steps with accountability."
    ),
    "Roast Me 💀": (
        "You are Roast Me 💀 for first-year students. "
        "Tone: witty, playful roast style, but classroom-safe and non-abusive. "
        "Roast behavior, not identity. End with useful advice. Keep it concise and funny."
    ),
}


def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.03)


def generate_response(user_input: str, system_prompt: str, mode: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    temperature = {
        "Chill 😌": 0.75,
        "Get Serious 🎯": 0.35,
        "Roast Me 💀": 1.0,
    }[mode]

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=temperature,
        max_tokens=220,
    )

    reply = (completion.choices[0].message.content or "").strip()
    if not reply:
        return "I could not generate a response. Try again."
    return reply


def init_state() -> None:
    if "last_mode" not in st.session_state:
        st.session_state.last_mode = None

    if "last_input" not in st.session_state:
        st.session_state.last_input = ""

    if "last_response" not in st.session_state:
        st.session_state.last_response = ""


def main() -> None:
    st.set_page_config(page_title="PersonaBot", page_icon="🤖", layout="centered")
    init_state()

    st.title("PersonaBot")
    st.markdown("### Try different modes and see how the same problem gets totally different responses 👀")

    mode = st.radio(
        "Personality Mode",
        list(MODE_CONFIG.keys()),
        horizontal=True,
    )

    if st.session_state.last_mode != mode:
        try:
            st.toast(f"{MODE_CONFIG[mode]['label']} {MODE_CONFIG[mode]['icon']}")
        except Exception:
            st.info(f"Switched to {MODE_CONFIG[mode]['label']} {MODE_CONFIG[mode]['icon']}")

        st.session_state.last_mode = mode

    st.caption(
        {
            "Chill 😌": "Calm advice, no stress",
            "Get Serious 🎯": "Straight to the point",
            "Roast Me 💀": "No mercy, college style 💀",
        }[mode]
    )

    starter_prompts = [
        "I procrastinate a lot",
        "I can't focus",
        "Motivate me",
        "I'm wasting time",
    ]

    st.write("Try a starter:")
    prompt_cols = st.columns(2)
    for i, prompt in enumerate(starter_prompts):
        with prompt_cols[i % 2]:
            if st.button(prompt, use_container_width=True):
                st.session_state["last_input"] = prompt
                st.rerun()

    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is missing in your .env file.")
        st.stop()

    user_input = st.chat_input("Say something...")

    if user_input:
        st.session_state.last_input = user_input

    if st.session_state.last_input:
        try:
            response = generate_response(
                st.session_state.last_input,
                PERSONALITY_PROMPTS[mode],
                mode,
            )
            st.session_state.last_response = response
        except Exception:
            st.session_state.last_response = "The assistant is temporarily unavailable. Please try again."

        with st.chat_message("user", avatar="🧑‍🎓"):
            st.write(st.session_state.last_input)

        bot_icon = MODE_CONFIG[mode]["icon"]
        with st.chat_message("assistant", avatar=bot_icon):
            st.write_stream(stream_text(st.session_state.last_response))


if __name__ == "__main__":
    main()
