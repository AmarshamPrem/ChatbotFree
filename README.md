# ChatbotFree

Simple local chatbot examples using the Groq API. This repo contains three frontends:

- `main.py` — minimal terminal chatbot demo
- `chat_gui.py` — Tkinter GUI with fallback to terminal mode when Tk isn't available
- `chat_tui.py` — Textual (terminal UI) frontend

Prerequisites
- Python 3.9+ (3.10+ recommended)
- A Groq API key set as `GROQ_API_KEY` in your environment or in a `.env` file

Quick setup (Windows)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # PowerShell
# or .\.venv\Scripts\activate  # CMD
```

2. Install dependencies:

```powershell
pip install groq python-dotenv textual
```

Notes:
- `tkinter` is part of the standard library on most Python installers. If `chat_gui.py` reports missing Tcl/Tk, install a full Python distribution that includes Tcl/Tk or set `TCL_LIBRARY`/`TK_LIBRARY` appropriately.
- `textual` is required for `chat_tui.py`.

Setting the API key

Create a `.env` file at the project root with:

```
GROQ_API_KEY=your_api_key_here
```

Running

- Terminal demo:

```powershell
python main.py
```

- Tkinter GUI (will fall back to terminal mode if Tk isn't available):

```powershell
python chat_gui.py
```

- Textual TUI:

```powershell
python chat_tui.py
```

Behavioral notes
- The code now warns when `GROQ_API_KEY` is missing instead of crashing immediately.
- Response parsing is made more robust to handle different shapes returned by the Groq client.

If you'd like, I can add a `requirements.txt` and a small test script, or run a quick syntax check in the environment.
