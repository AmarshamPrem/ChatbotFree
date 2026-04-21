import tkinter as tk
from tkinter import scrolledtext, ttk
from groq import Groq
import os
import sys


class ChatGUI:
    def __init__(self):
        # Create client and basic state regardless of UI availability
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.models = ["llama-3.3-70b-versatile", "qwen/qwen3-32b"]
        self.model = self.models[0]
        self.messages = []

        # Try to initialize Tk; if Tcl/Tk isn't available, fall back to CLI mode
        try:
            self.root = tk.Tk()
        except tk.TclError as e:
            print("Warning: Tkinter/Tcl not available or misconfigured. Falling back to terminal mode.", file=sys.stderr)
            print("Details:", e, file=sys.stderr)
            print("If you want the GUI, install a full Python distribution with Tcl/Tk or set TCL_LIBRARY/TK_LIBRARY environment variables.", file=sys.stderr)
            self.use_cli = True
            self.root = None
            return

        self.use_cli = False
        self.root.title("Groq Chatbot")
        self.root.geometry("600x500")

        self.setup_ui()

    def setup_ui(self):
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Model selector
        model_frame = tk.Frame(self.root)
        model_frame.pack(pady=5)
        tk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value=self.model)
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, values=self.models, state="readonly")
        model_combo.pack(side=tk.LEFT, padx=5)
        model_combo.bind("<<ComboboxSelected>>", self.change_model)

        # Input frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.entry = tk.Entry(input_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.send_message)

        send_btn = tk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side=tk.RIGHT)

        self.add_message("Bot", "Chat started. Pick a model and type!")

    def change_model(self, event=None):
        self.model = self.model_var.get()

    def add_message(self, sender, msg):
        # If in CLI fallback, print messages to stdout
        if getattr(self, "use_cli", False):
            print(f"{sender}: {msg}\n")
            return

        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {msg}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def send_message(self, event=None):
        # GUI path: event comes from tkinter
        if getattr(self, "use_cli", False):
            return  # CLI mode uses run_cli

        msg = self.entry.get().strip()
        if msg:
            self.entry.delete(0, tk.END)
            self.add_message("You", msg)
            self.messages.append({"role": "user", "content": msg})

            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                )

                # Robust parsing for different response shapes
                reply = None
                # object-like access
                try:
                    choices = getattr(resp, "choices", None)
                    if choices and len(choices) > 0:
                        choice = choices[0]
                        # try message.content
                        msg_obj = getattr(choice, "message", None)
                        if msg_obj is not None:
                            reply = getattr(msg_obj, "content", None) or str(msg_obj)
                        # fallback to text
                        if reply is None:
                            reply = getattr(choice, "text", None)
                except Exception:
                    reply = None

                # dict-like access fallback
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

                self.messages.append({"role": "assistant", "content": reply})
                self.add_message("Bot", reply)

            except Exception as e:
                # show error in chat instead of crashing
                self.add_message("Bot", f"Error: {e}")

    def run_cli(self):
        print("Groq Chatbot (terminal mode). Type 'exit' or Ctrl+D to quit.")
        print(f"Available models: {', '.join(self.models)}")
        print(f"Current model: {self.model}")
        try:
            while True:
                try:
                    msg = input("You: ").strip()
                except EOFError:
                    print("\nExiting.")
                    break
                if not msg:
                    continue
                if msg.lower() in ("exit", "quit"):
                    print("Exiting.")
                    break
                # allow switching model by prefix: /model <model-name>
                if msg.startswith("/model "):
                    candidate = msg.split(None, 1)[1].strip()
                    if candidate in self.models:
                        self.model = candidate
                        print(f"Switched to model: {self.model}")
                    else:
                        print(f"Unknown model: {candidate}")
                    continue

                self.messages.append({"role": "user", "content": msg})
                try:
                    resp = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages,
                    )
                    # parse reply robustly (same logic as GUI)
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

                    self.messages.append({"role": "assistant", "content": reply})
                    print(f"Bot: {reply}\n")
                except Exception as e:
                    print(f"Error: {e}", file=sys.stderr)

        except KeyboardInterrupt:
            print("\nExiting.")

    def run(self):
        if getattr(self, "use_cli", False):
            self.run_cli()
            return
        self.root.mainloop()


if __name__ == "__main__":
    app = ChatGUI()
    app.run()