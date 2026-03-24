import os
import re
from typing import Dict, List

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
MAX_HISTORY_MESSAGES = 8

PERSONALITY_PROMPTS: Dict[str, str] = {
    "chill_friend": (
        "You are 'The Chill Friend' for a live student demo. "
        "Personality: relaxed, supportive, like a close friend who keeps things simple. "

        "Tone: casual and natural. You can understand slang and informal language, "
        "and you may occasionally use light slang (like 'nah you're good', 'you got this'), "
        "but never overdo it or sound forced. "

        "Behavior: reduce stress, make things feel manageable. "
        "If the user is stuck or overthinking, calm them first, then guide them. "
        "Focus on small, easy steps instead of big plans. "

        "Style rules: short responses (2–4 lines), no formal structure, no headings. "

        "Output pattern: "
        "1) Friendly, relatable line "
        "2) One simple next step. "

        "Example vibe: 'Nah you're overthinking this. Just start small—10 mins and you're good.'"
    ),

    "strict_professor": (
        "You are 'The Strict Mentor' for a live student demo. "
        "Personality: disciplined, direct, results-focused. "

        "Tone: serious, precise, no slang, no fluff. Slightly intimidating but fair. "

        "Behavior: identify the real problem, correct it, and enforce action. "
        "Do not comfort unnecessarily. Focus on accountability. "

        "Style rules: always structured and concise. "

        "Output format MUST be: "
        "Assessment: (core issue) "
        "Correction: (what must change) "
        "Action Steps: (clear numbered steps)."
    ),

    "savage_roast": (
        "You are 'The Savage Coach' for a classroom-safe live demo. "
        "Personality: sharp, funny, sarcastic, slightly dramatic. "

        "Tone: playful roasting with modern casual language. "
        "You understand slang and can use light slang occasionally, "
        "but keep it clean, clever, and not excessive. "

        "Behavior: call out excuses in a funny way, then give real advice. "
        "Roast the behavior, never the person. No offensive or sensitive content. "

        "Style rules: punchy, energetic, not too long. "

        "Output format MUST be: "
        "Roast: (funny callout) "
        "Reality Check: (what’s actually happening) "
        "Power Move: (clear action). "

        "Example vibe: 'Bro said he'll start “tomorrow” like tomorrow isn’t booked for the past 3 weeks 💀'"
    ),
}

TEMPERATURE_BY_PERSONALITY: Dict[str, float] = {
    "chill_friend": 0.75,
    "strict_professor": 0.35,
    "savage_roast": 1.0,
}

LABELS = {
    "chill_friend": "Chill",
    "strict_professor": "Get Serious",
    "savage_roast": "Roast Me",
}


def init_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "personality" not in st.session_state:
        st.session_state.personality = "chill_friend"
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}
    if "busy" not in st.session_state:
        st.session_state.busy = False


def update_user_profile_from_message(user_message: str) -> None:
    name_match = re.search(
        r"\b(?:my name is|i am|i'm)\s+([A-Za-z][A-Za-z\-']{1,30})\b",
        user_message,
        flags=re.IGNORECASE,
    )
    if name_match:
        st.session_state.user_profile["name"] = name_match.group(1)


def build_memory_context() -> str:
    profile = st.session_state.user_profile
    if profile.get("name"):
        return f"User name: {profile['name']}"
    return "No known user details yet."


def handle_memory_queries(user_message: str, personality: str) -> str:
    lowered = user_message.lower()
    profile = st.session_state.user_profile
    history = st.session_state.history

    asks_name = any(
        pattern in lowered
        for pattern in ["what is my name", "do you know my name", "who am i", "what's my name"]
    )
    if asks_name:
        remembered_name = profile.get("name")
        if remembered_name:
            if personality == "strict_professor":
                return (
                    "Assessment:\nI retain your provided detail.\n\n"
                    f"Correction:\nNone required. Your name is {remembered_name}.\n\n"
                    "Action Steps:\nProceed with your next question."
                )
            if personality == "savage_roast":
                return (
                    "Roast: You expected me to forget already? Bold move.\n\n"
                    f"Reality Check: Your name is {remembered_name}.\n\n"
                    "Power Move: Ask me to use your name in every reply and own the main-character energy."
                )
            return (
                f"Hey, I remember you. Your name is {remembered_name}.\n"
                "You got this, keep the questions coming."
            )

        if personality == "strict_professor":
            return (
                "Assessment:\nInsufficient data.\n\n"
                "Correction:\nYou have not provided your name in this session.\n\n"
                "Action Steps:\nState it clearly, for example: 'My name is Alex.'"
            )
        if personality == "savage_roast":
            return (
                "Roast: Memory test before introductions? Ambitious.\n\n"
                "Reality Check: You never gave me your name.\n\n"
                "Power Move: Drop it now like, 'My name is Alex,' and I will lock it in."
            )
        return "I do not have your name yet. Tell me with 'My name is ...' and I will remember it."

    asks_earlier = any(
        pattern in lowered
        for pattern in [
            "what did i say earlier",
            "what did i tell you earlier",
            "what was my previous message",
            "what did i say before",
        ]
    )
    if asks_earlier:
        user_only = [m["content"] for m in history if m.get("role") == "user"]
        recent = user_only[-3:]
        if recent:
            if personality == "strict_professor":
                bullet_lines = "\n".join(f"- {item}" for item in recent)
                return (
                    "Assessment:\nYou asked for recall of prior input.\n\n"
                    f"Correction:\nYour recent messages were:\n{bullet_lines}\n\n"
                    "Action Steps:\nSpecify which point you want expanded."
                )
            if personality == "savage_roast":
                bullet_lines = "\n".join(f"- {item}" for item in recent)
                return (
                    "Roast: Rewind requested. Director's cut activated.\n\n"
                    f"Reality Check:\nHere is what you said recently:\n{bullet_lines}\n\n"
                    "Power Move: Pick one and I will turn it into a killer answer."
                )
            joined = "\n".join(f"- {item}" for item in recent)
            return f"Yep, here is what you said recently:\n{joined}\nWant me to build on one of these?"

        if personality == "strict_professor":
            return (
                "Assessment:\nNo prior user messages found.\n\n"
                "Correction:\nA recall request requires earlier content.\n\n"
                "Action Steps:\nSend a few messages first, then ask again."
            )
        if personality == "savage_roast":
            return (
                "Roast: You asked for a flashback with no footage recorded.\n\n"
                "Reality Check: There are no earlier user messages yet.\n\n"
                "Power Move: Drop a few prompts and run the memory test again."
            )
        return "I do not have earlier messages yet. Send a few prompts first, then ask again."

    return ""


def build_messages(user_message: str, personality: str, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    memory_context = build_memory_context()
    return [
        {"role": "system", "content": PERSONALITY_PROMPTS[personality]},
        {
            "role": "system",
            "content": (
                "Use known memory naturally when relevant. "
                "Do not invent personal facts. "
                f"Known memory: {memory_context}"
            ),
        },
        *history,
        {"role": "user", "content": user_message},
    ]


def ask_groq(user_message: str, personality: str, history: List[Dict[str, str]]) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    messages = build_messages(user_message=user_message, personality=personality, history=history)

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=TEMPERATURE_BY_PERSONALITY[personality],
        max_tokens=320,
    )
    assistant_reply = (completion.choices[0].message.content or "").strip()
    if not assistant_reply:
        return "I could not generate a response. Please try again."
    return assistant_reply


def render_header() -> None:
    st.markdown("### PersonaBot")
    st.caption("Pick a vibe, then ask anything.")

    cols = st.columns([4, 1])
    with cols[0]:
        st.session_state.personality = st.radio(
            "Personality Mode",
            options=list(LABELS.keys()),
            format_func=lambda key: LABELS[key],
            horizontal=True,
            index=list(LABELS.keys()).index(st.session_state.personality),
            disabled=st.session_state.busy,
        )
    with cols[1]:
        if st.button("Reset Chat", use_container_width=True, disabled=st.session_state.busy):
            st.session_state.history = []
            st.session_state.user_profile = {}
            st.rerun()


def main() -> None:
    st.set_page_config(page_title="PersonaBot", page_icon="🤖", layout="centered")
    init_state()
    render_header()

    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is missing in your .env file.")
        st.stop()

    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_message = st.chat_input("Ask anything...", disabled=st.session_state.busy)
    if not user_message:
        return

    st.session_state.busy = True
    update_user_profile_from_message(user_message)

    st.session_state.history.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    try:
        memory_reply = handle_memory_queries(user_message=user_message, personality=st.session_state.personality)

        if memory_reply:
            assistant_reply = memory_reply
        else:
            with st.chat_message("assistant"):
                with st.spinner("PersonaBot is typing..."):
                    assistant_reply = ask_groq(
                        user_message=user_message,
                        personality=st.session_state.personality,
                        history=st.session_state.history[:-1][-MAX_HISTORY_MESSAGES:],
                    )
                    st.markdown(assistant_reply)

        if memory_reply:
            with st.chat_message("assistant"):
                st.markdown(assistant_reply)

        st.session_state.history.append({"role": "assistant", "content": assistant_reply})
        st.session_state.history = st.session_state.history[-MAX_HISTORY_MESSAGES:]

    except Exception:
        with st.chat_message("assistant"):
            st.error("The assistant is temporarily unavailable. Please try again in a moment.")
    finally:
        st.session_state.busy = False


if __name__ == "__main__":
    main()
