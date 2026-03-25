import os
import time
from typing import Dict

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

MODE_CONFIG = {
    "chill": {"icon": "smiley", "label": "Chill Mode", "display": "Chill"},
    "serious": {"icon": "target", "label": "Serious Mode", "display": "Get Serious"},
    "roast": {"icon": "skull", "label": "Roast Mode", "display": "Roast Me"},
}

PERSONALITY_PROMPTS: Dict[str, str] = {
    "chill": (
        "You are Chill for college students. "
        "Tone: warm, casual, friendly, low-pressure. "
        "Keep responses short and practical. Use encouragement."
        "Responses should be 1-4 lines"
    ),
    "serious": (
        "You are Get Serious for college students. "
        "Tone: direct, structured, no fluff. "
        "Give concise, actionable steps with accountability."
        "Responses should be 1-2 lines"
    ),
    "roast": (
        "You are Roast Me for college students. "
        "Tone: witty, playful roast style, but classroom-safe and non-abusive. "
        "Roast behavior, not identity. End with useful advice. Keep it concise and funny."
        "Responses should be 1-2 lines"
    ),
}


def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.03)


def generate_response(user_input: str, system_prompt: str, mode: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    temperature = {
        "chill": 0.75,
        "serious": 0.35,
        "roast": 1.0,
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

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "queued_input" not in st.session_state:
        st.session_state.queued_input = None


def main() -> None:
    st.set_page_config(page_title="PersonaBot", layout="centered")
    init_state()

    st.markdown(
        '<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css">',
        unsafe_allow_html=True,
    )

    st.markdown('<h1><i class="ph ph-robot" aria-hidden="true"></i> PersonaBot</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="margin-top: -0.5rem;">Try different modes and see how the same problem gets totally different responses.</p>',
        unsafe_allow_html=True,
    )

    mode = st.radio(
        "Personality Mode",
        list(MODE_CONFIG.keys()),
        format_func=lambda mode_key: MODE_CONFIG[mode_key]["display"],
        horizontal=True,
    )

    if st.session_state.last_mode != mode:
        try:
            st.toast(f"{MODE_CONFIG[mode]['label']} enabled")
        except Exception:
            st.info(f"Switched to {MODE_CONFIG[mode]['label']}")

        st.session_state.last_mode = mode

    st.markdown(
        {
            "chill": '<span><i class="ph ph-smiley" aria-hidden="true"></i> Calm advice, no stress</span>',
            "serious": '<span><i class="ph ph-target" aria-hidden="true"></i> Straight to the point</span>',
            "roast": '<span><i class="ph ph-skull" aria-hidden="true"></i> No mercy, college style</span>',
        }[mode],
        unsafe_allow_html=True,
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
                st.session_state.queued_input = prompt
                st.rerun()

    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is missing in your .env file.")
        st.stop()

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                icon = MODE_CONFIG[message["mode"]]["icon"]
                display = MODE_CONFIG[message["mode"]]["display"]
                st.markdown(
                    f'<span><i class="ph ph-{icon}" aria-hidden="true"></i> {display}</span>',
                    unsafe_allow_html=True,
                )
            st.write(message["text"])

    user_input = st.chat_input("Say something...")
    incoming_text = user_input or st.session_state.queued_input
    st.session_state.queued_input = None

    if incoming_text:
        st.session_state.chat_history.append(
            {"role": "user", "text": incoming_text, "mode": mode}
        )

        with st.chat_message("user"):
            st.write(incoming_text)

        try:
            response = generate_response(
                incoming_text,
                PERSONALITY_PROMPTS[mode],
                mode,
            )
        except Exception:
            response = "The assistant is temporarily unavailable. Please try again."

        st.session_state.chat_history.append(
            {"role": "assistant", "text": response, "mode": mode}
        )

        with st.chat_message("assistant"):
            st.markdown(
                f'<span><i class="ph ph-{MODE_CONFIG[mode]["icon"]}" aria-hidden="true"></i> {MODE_CONFIG[mode]["display"]}</span>',
                unsafe_allow_html=True,
            )
            st.write_stream(stream_text(response))


if __name__ == "__main__":
    main()
