# ⚡ Groq Chatbot — Streamlit

A multi-turn conversational AI chatbot built with **Python + Streamlit + Groq**.  
Streams responses in real-time, maintains full chat history, and requires zero frontend code.

---

## Project Structure

```
groq-streamlit-agent/
├── app.py                   # Main Streamlit app
├── requirements.txt         # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit theme config
└── README.md
```

---

## Quick Start

### 1. Clone / download the project

```bash
cd groq-streamlit-agent
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get a Groq API Key

Sign up free at [console.groq.com](https://console.groq.com) → API Keys → Create Key.  
Keys start with `gsk_`.

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.  
Enter your API key in the sidebar and start chatting!

---

## Features

| Feature | Details |
|---|---|
| Multi-turn memory | Full conversation history sent every request |
| Streaming | Token-by-token streaming with live cursor |
| Model picker | Llama 3.3 70B · Llama 3.1 8B · Mixtral · Gemma 2 |
| Temperature | Slider from 0.0 (focused) to 2.0 (creative) |
| Max tokens | 256 / 512 / 1024 / 2048 / 4096 |
| System prompt | Editable in sidebar, persists across turns |
| Chat stats | Turn count + token usage displayed live |
| Error handling | API key, rate limit, model errors shown clearly |
| Clear chat | Resets history and token counter |

---

## Available Models

| Display Name | Model ID | Best For |
|---|---|---|
| Llama 3.3 · 70B | `llama-3.3-70b-versatile` | General use, best quality |
| Llama 3.1 · 8B | `llama-3.1-8b-instant` | Speed, simple tasks |
| Mixtral · 8x7B | `mixtral-8x7b-32768` | Long contexts (32K) |
| Gemma 2 · 9B | `gemma2-9b-it` | Instruction following |

---

## How Multi-Turn Works

Each API call sends the **entire conversation history** plus the system prompt:

```python
api_messages = [
    {"role": "system",    "content": "You are a helpful assistant."},
    {"role": "user",      "content": "Hello!"},
    {"role": "assistant", "content": "Hi there! How can I help?"},
    {"role": "user",      "content": "What is Groq?"},   # ← new message
]
```

The model sees all previous turns, enabling coherent multi-turn dialogue.  
History is stored in `st.session_state.messages` (resets on page refresh or "Clear chat").

---

## Extending the App

### Save API key to environment variable (avoid typing each time)

```bash
export GROQ_API_KEY="gsk_your_key_here"
```

Then in `app.py`, auto-load it:
```python
import os
api_key = os.getenv("GROQ_API_KEY", "")
```

### Export conversation to JSON

```python
import json
st.sidebar.download_button(
    label="Export chat",
    data=json.dumps(st.session_state.messages, indent=2),
    file_name="conversation.json",
    mime="application/json",
)
```

### Add a `.env` file (using python-dotenv)

```bash
pip install python-dotenv
```

Create `.env`:
```
GROQ_API_KEY=gsk_your_key_here
```

Load in `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GROQ_API_KEY", "")
```

---

## Requirements

- Python 3.9+
- Internet connection (for Groq API calls)
- Free Groq account

---

## License

MIT — free to use and modify.
