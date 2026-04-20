"""
Groq Multi-Turn Conversational Chatbot
Built with Streamlit + Groq API (OpenAI-compatible)
API key loaded securely from .env file
"""

import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# ── Load environment variables from .env ──────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Groq Chatbot",
    page_icon="⚡",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #f8f8f6; }
    [data-testid="stSidebar"] h2 { font-size: 1.1rem; }
    [data-testid="stChatMessage"] { border-radius: 10px; padding: 4px 0; }
    [data-testid="stChatInputContainer"] textarea { border-radius: 10px; }
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #ddd;
        background: #fff;
        color: #333;
    }
    div.stButton > button:hover { background: #f0f0f0; }
</style>
""", unsafe_allow_html=True)


# ── Constants ─────────────────────────────────────────────────────────────────
AVAILABLE_MODELS = {
    "Llama 3.3 · 70B (recommended)": "llama-3.3-70b-versatile",
    "Llama 3.1 · 8B (fastest)":      "llama-3.1-8b-instant",
    "Mixtral · 8x7B (long context)":  "mixtral-8x7b-32768",
    "Gemma 2 · 9B":                   "gemma2-9b-it",
}

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, concise, and friendly AI assistant. "
    "Engage naturally in conversation while being accurate and clear."
)


# ── Session state initialisation ──────────────────────────────────────────────
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0

init_session()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚡ Groq Chatbot")
    st.caption("Multi-turn · Streaming · OpenAI-compatible")
    st.divider()

    # Model selection
    st.subheader("🤖 Model")
    model_label = st.selectbox("Choose a model", list(AVAILABLE_MODELS.keys()))
    selected_model = AVAILABLE_MODELS[model_label]

    # Parameters
    st.subheader("⚙️ Parameters")
    temperature = st.slider(
        "Temperature", 0.0, 2.0, 0.7, 0.1,
        help="Higher = more creative, lower = more focused",
    )
    max_tokens = st.select_slider(
        "Max tokens per reply",
        options=[256, 512, 1024, 2048, 4096],
        value=1024,
    )

    st.divider()

    # System prompt
    st.subheader("📋 System Prompt")
    system_prompt = st.text_area(
        "Instruction for the assistant",
        value=st.session_state.system_prompt,
        height=130,
        placeholder="You are a helpful assistant...",
    )
    if system_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = system_prompt

    st.divider()

    # Stats + clear
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Turns", len(st.session_state.messages))
    with col2:
        st.metric("Tokens used", st.session_state.total_tokens)

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.rerun()


# ── Guard: stop app if key is missing ────────────────────────────────────────
if not GROQ_API_KEY:
    st.error("❌ **GROQ_API_KEY not found.** Add it to your `.env` file and restart the app.")
    st.stop()

# ── Main chat area ────────────────────────────────────────────────────────────
st.title("💬 Chat")

if not st.session_state.messages:
    st.info("👋 Hi! Start chatting below.", icon="⚡")

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Type your message…")

if user_input:
    # 1. Show user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Call Groq with full conversation history (multi-turn)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            client = Groq(api_key=GROQ_API_KEY)

            # System prompt + entire history sent every request
            api_messages = [{"role": "system", "content": st.session_state.system_prompt}]
            api_messages += st.session_state.messages

            stream = client.chat.completions.create(
                model=selected_model,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            # Stream tokens as they arrive
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                placeholder.markdown(full_response + "▌")

            # Final render — remove streaming cursor
            placeholder.markdown(full_response)

            # Track token usage if available
            if hasattr(chunk, "x_groq") and chunk.x_groq and chunk.x_groq.usage:
                st.session_state.total_tokens += chunk.x_groq.usage.total_tokens

        except Exception as e:
            error_msg = str(e)
            if "invalid_api_key" in error_msg.lower() or "401" in error_msg:
                full_response = "❌ **Invalid API key.** Check `GROQ_API_KEY` in your `.env` file."
            elif "rate_limit" in error_msg.lower() or "429" in error_msg:
                full_response = "⏳ **Rate limit hit.** Please wait a moment and try again."
            elif "model_not_found" in error_msg.lower():
                full_response = f"❌ **Model not found:** `{selected_model}`. Try a different model."
            else:
                full_response = f"❌ **Error:** {error_msg}"
            placeholder.markdown(full_response)

        # 3. Save assistant reply to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
        })