You are a senior full-stack engineer and AI product designer.

Generate a COMPLETE, RUNNABLE chatbot web application for a live demo.

This is NOT a toy. It must feel polished, responsive, and impressive.

---

# 🎯 OBJECTIVE

Build a chatbot that:
- Has a clean modern chat interface
- Supports multiple personality modes (visibly different behavior)
- Remembers recent conversation (context awareness)
- Uses OpenAI API properly
- Is extremely simple to run locally

This will be used to impress first-year students in a live demo.

---

# ⚙️ TECH STACK (STRICT)

Backend:
- Python (Flask)

Frontend:
- HTML
- CSS (modern styling)
- Vanilla JavaScript (no frameworks)

---

# 📁 PROJECT STRUCTURE

Generate ALL files:

project/
│
├── app.py
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js

All files must be COMPLETE and WORKING.

---

# 🧠 CORE FEATURES

## 1. Chat UI
- Chat bubbles (user vs assistant)
- Smooth scrolling
- Input box + send button
- Clean, modern UI (dark mode preferred)
- Responsive layout

---

## 2. PERSONALITY MODES (CRITICAL FEATURE)

Add 3 toggle buttons in UI:

1. Chill Friend  
2. Strict Professor  
3. Savage Roast  

Switching modes MUST change AI behavior clearly.

---

## 3. SYSTEM PROMPTS (VERY IMPORTANT)

Define strong, well-written system prompts:

### Chill Friend
- Friendly, supportive, casual
- Encouraging tone
- Uses simple language

### Strict Professor
- Formal, structured, slightly intimidating
- Gives precise answers
- Corrects user when needed

### Savage Roast
- Funny, sarcastic, roasts user
- NOT offensive or abusive
- Should be entertaining and safe

Store prompts in backend cleanly.

---

## 4. MEMORY SYSTEM

- Store last 5–8 messages in a list
- Send full conversation history to OpenAI
- Bot should recall previous messages naturally

---

## 5. BACKEND (Flask)

Routes:

GET `/`
→ serve HTML

POST `/chat`
→ receives:
   - message
   - selected personality

→ returns:
   - AI response

---

## 6. OPENAI INTEGRATION

- Use latest OpenAI Python SDK
- Load API key from environment variable
- Use chat completion API
- Proper message format:
  - system prompt
  - conversation history
  - user input

Handle errors gracefully.

---

## 7. FRONTEND LOGIC

- Send message via fetch API
- Update chat dynamically (no reload)
- Show loading indicator while waiting
- Handle personality switching

---

## 8. UX DETAILS (IMPORTANT)

- Highlight active personality button
- Auto-scroll chat
- Clear input after send
- Basic animations (optional but clean)

---

# 🧾 REQUIREMENTS.TXT

Include all required dependencies.

---

# 🔐 ENV FILE

Provide `.env.example` with:

OPENAI_API_KEY=your_key_here

---

# 🚀 SETUP INSTRUCTIONS

Include clear steps:

1. install dependencies
2. add API key
3. run server
4. open browser

---

# 🎤 DEMO-OPTIMIZED BEHAVIOR

Make sure:
- Responses are fast
- Personalities are clearly different
- Memory works visibly

---

# ⚠️ CONSTRAINTS

- NO placeholders
- NO pseudo code
- NO missing parts
- Everything must run without modification
- Keep code beginner-friendly but clean

---

# 🧠 OUTPUT FORMAT

Provide:

1. Project structure
2. Each file with full code
3. Setup instructions
4. How to demonstrate features

---

Build this like a real product, not a tutorial.