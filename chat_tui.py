from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Button, Select
from textual.containers import VerticalScroll, Container
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class Message(Label):
    def __init__(self, text: str, is_user: bool):
        # Use a Label as the message widget for compatibility across Textual versions
        classes = "message" if is_user else "bot-message"
        super().__init__(text, classes=classes)
        
class ChatApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #chat-history {
        height: 1fr;
        overflow-y: auto;
    }
    #input-container {
        height: 1;
        layout: horizontal;
    }
    .message { 
        margin-left: 50%; 
        color: cyan;
    }
    .bot-message { 
        margin-right: 50%; 
        color: green;
    }
    """

    def __init__(self):
        super().__init__()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not set. Chat will not work until you set it.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
        self.models = ["llama-3.3-70b-versatile", "qwen/qwen3-32b"]
        self.model = self.models[0]
        self.messages = []

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="chat-history")
        yield Container(
            Select([(m, m) for m in self.models], id="model-select"),
            Input(placeholder="Type message...", id="input"),
            Button("Send", id="send"),
            id="input-container"
        )

    def on_mount(self):
        self.query_one("#input").focus()

    def on_select(self, event):
        # Textual's Select event class names vary by version; avoid referencing
        # Select.Selected directly. Instead, read the current value from the
        # Select widget using its id so this works across versions.
        try:
            sel = self.query_one("#model-select", Select)
            # Prefer `value` attribute if present
            self.model = getattr(sel, "value", None) or getattr(sel, "prompt", None) or str(sel)
        except Exception:
            # fallback: do nothing if we can't determine selection
            pass

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send":
            self.send_message()

    def on_input_submitted(self, event: Input.Submitted):
        self.send_message()

    def send_message(self):
        input_widget = self.query_one("#input", Input)
        msg = input_widget.value.strip()
        if not msg:
            return
        input_widget.value = ""

        # Add user message
        self.query_one("#chat-history", VerticalScroll).mount(Message(msg, True))
        self.messages.append({"role": "user", "content": msg})

        # Get response
        try:
            if self.client is None:
                raise RuntimeError("GROQ_API_KEY not configured; cannot send request")

            resp = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
            )

            # robust parse
            reply = None
            try:
                choices = getattr(resp, "choices", None)
                if choices and len(choices) > 0:
                    choice = choices[0]
                    msg_obj = getattr(choice, "message", None)
                    if msg_obj is not None:
                        reply = getattr(msg_obj, "content", None) or str(msg_obj)
                    if reply is None:
                        reply = getattr(choice, "text", None)
            except Exception:
                reply = None

            if reply is None:
                try:
                    reply = resp["choices"][0]["message"]["content"]
                except Exception:
                    try:
                        reply = resp["choices"][0].get("text")
                    except Exception:
                        reply = str(resp)

            if isinstance(reply, (list, dict)):
                reply = str(reply)

        except Exception as e:
            reply = f"Error: {e}"
        self.messages.append({"role": "assistant", "content": reply})

        # Add bot message
        self.query_one("#chat-history", VerticalScroll).mount(Message(reply, False))

if __name__ == "__main__":
    app = ChatApp()
    app.run()