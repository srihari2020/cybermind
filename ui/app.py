import csv
import io
import re
from typing import Optional, Tuple
import requests
import streamlit as st

# ============================================================
# 1. APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(page_title="CyberMind", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "cybermind-4b"
MAX_FILE_SIZE_BYTES = 200 * 1024
MAX_FILE_CONTEXT_CHARS = 12_000
MAX_HISTORY_MESSAGES = 20
OLLAMA_TIMEOUT_SECONDS = (5, 300)

# ============================================================
# 2. SYSTEM PROMPTS & INTENT ROUTING
# ============================================================

CASUAL_PROMPT = """You are CyberMind, a friendly Tier-3 SOC Analyst. 
The user is making casual conversation. Reply naturally and briefly in 1 to 3 sentences. 
DO NOT use any strict formatting, headers, or lesson structures."""

STRICT_TEACHER_PROMPT = """You are CyberMind, an expert Cybersecurity Teacher and Tier-3 SOC Analyst.
You MUST format your response using EXACTLY the structure below. Do not skip the Ethics line. Provide MULTIPLE highly detailed bullet points for every phase.

### EXACT RESPONSE FORMAT EXAMPLE:
Welcome to your lesson! **[Topic]** is [1-2 sentence rich definition].

**Ethics**: *Only investigate or test systems you own.*

### Phase 1: Core Analysis
* **Primary Mechanism**: Explain exactly how this concept or threat works in detail.
* **Key Indicators**: Detail the specific signs, ports, or behaviors associated with it.
* **Impact**: Explain what happens if this vulnerability is successfully exploited.

### Phase 2: Tactical Mitigation
* **Defensive Action 1**: Specify the exact tool, configuration change, or command to fix it.
* **Defensive Action 2**: Explain monitoring or secondary prevention strategies.
"""

def detect_intent(query: str, has_file: bool = False) -> str:
    query_lower = query.strip().lower()
    lesson_triggers = ["teach", "explain", "how", "what", "analyze", "log", "vulnerability", "hack", "phase", "cve", "mitre", "attack"]
    
    if len(query_lower.split()) > 4 or any(trigger in query_lower for trigger in lesson_triggers) or has_file:
        return STRICT_TEACHER_PROMPT
    return CASUAL_PROMPT

# ============================================================
# 3. STREAMLIT SESSION STATE
# ============================================================

if "chats" not in st.session_state:
    st.session_state.chats = {"Session 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Session 1"
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1
if "uploaded_context" not in st.session_state:
    st.session_state.uploaded_context = None
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

# ============================================================
# 4. PAGE STYLING
# ============================================================

st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    h1, h2, h3, h4 { color: #e6edf3; }
    p, li { color: #c9d1d9; line-height: 1.65; }
    code { color: #79c0ff; }
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 5. SIDEBAR
# ============================================================

with st.sidebar:
    st.title("🛡️ CyberMind")
    st.caption("Local AI cybersecurity assistant")

    if st.button("➕ New chat", use_container_width=True):
        st.session_state.chat_counter += 1
        new_name = f"Session {st.session_state.chat_counter}"
        st.session_state.chats[new_name] = []
        st.session_state.current_chat = new_name

    st.markdown("---")
    st.subheader("Previous chats")
    for chat_name in reversed(list(st.session_state.chats.keys())):
        is_current = chat_name == st.session_state.current_chat
        button_label = f"🟢 {chat_name}" if is_current else f"💬 {chat_name}"
        if st.button(button_label, key=f"select_{chat_name}", use_container_width=True, disabled=is_current):
            st.session_state.current_chat = chat_name

    st.markdown("---")
    st.subheader("📂 Threat intelligence")
    uploaded_file = st.file_uploader("Upload .log, .txt, or .csv", type=["log", "txt", "csv"], help="Maximum file size: 200 KB.")
    
    if uploaded_file is not None:
        try:
            raw = uploaded_file.getvalue()
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = raw.decode("utf-8", errors="replace")
                
            filename = uploaded_file.name.lower()
            if filename.endswith(".csv"):
                rows = list(csv.reader(io.StringIO(text)))
                text = "\n".join(" | ".join(row) for row in rows)
                
            st.session_state.uploaded_context = text[:MAX_FILE_CONTEXT_CHARS]
            st.session_state.uploaded_filename = uploaded_file.name
            st.success(f"Loaded: {uploaded_file.name}")
        except Exception as exc:
            st.error(f"Error reading file: {exc}")

    st.markdown("---")
    if st.button("🗑️ Clear current chat", use_container_width=True):
        st.session_state.chats[st.session_state.current_chat] = []
        st.session_state.uploaded_context = None
        st.session_state.uploaded_filename = None

    st.caption("Engine: Ollama | Model: CyberMind-4B")

# ============================================================
# 6. MAIN CHAT
# ============================================================

st.title("🛡️ CyberMind")
st.caption("Ask about cybersecurity, Linux, programming, networking, troubleshooting, or defensive security.")

active_history = st.session_state.chats[st.session_state.current_chat]

for message in active_history:
    display_text = message["content"].split("\n\n[SYSTEM INJECTION]")[0]
    avatar = "👤" if message["role"] == "user" else "🛡️"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(display_text)

query = st.chat_input("Message CyberMind...")

if query:
    query = query.strip()
    if not query:
        st.stop()

    mode_prompt = detect_intent(query, has_file=bool(st.session_state.uploaded_context))
    user_content = query

    if st.session_state.uploaded_context:
        user_content += (
            f"\n\n[SYSTEM INJECTION]\n[LOG FILE DATA / EVIDENCE]:\n```\n"
            f"{st.session_state.uploaded_context[:3000]}\n```\n"
            "[CRITICAL DIRECTIVE: Analyze the intelligence above.]"
        )

    request_messages = [{"role": "system", "content": mode_prompt}] + active_history[-MAX_HISTORY_MESSAGES:] + [{"role": "user", "content": user_content}]

    with st.chat_message("user", avatar="👤"):
        st.markdown(query)

    active_history.append({"role": "user", "content": user_content})

    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("CyberMind is analyzing..."):
            try:
                response = requests.post(
                    OLLAMA_CHAT_URL,
                    json={
                        "model": DEFAULT_MODEL,
                        "messages": request_messages,
                        "stream": False,
                        "options": {"temperature": 0.3, "top_p": 0.9, "repeat_penalty": 1.15}
                    },
                    timeout=OLLAMA_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                answer = response.json().get("message", {}).get("content", "").strip()
                
                st.markdown(answer)
                active_history.append({"role": "assistant", "content": answer})

            except Exception as exc:
                error_text = f"Connection Error: {exc}"
                st.error(error_text)
                active_history.append({"role": "assistant", "content": error_text})
