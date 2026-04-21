from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Button, Select
from textual.containers import VerticalScroll, Container
from groq import Groq
import os

class Message(Container):
    def __init__(self, text: str, is_user: bool):
        self.is_user = is_user
        super().__init__(Label(text), classes="message" if is_user else "bot-message")

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
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
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
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )
        reply = resp.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})

        # Add bot message
        self.query_one("#chat-history", VerticalScroll).mount(Message(reply, False))

if __name__ == "__main__":
    app = ChatApp()
    app.run()