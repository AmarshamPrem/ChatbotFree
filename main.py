import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

models = ["llama-3.3-70b-versatile", "qwen/qwen3-32b"]

def extract_reply(resp):
    try:
        choices = getattr(resp, "choices", None)
        if choices and len(choices) > 0:
            choice = choices[0]
            msg_obj = getattr(choice, "message", None)
            if msg_obj is not None:
                return getattr(msg_obj, "content", None) or str(msg_obj)
            text = getattr(choice, "text", None)
            if text:
                return text
    except Exception:
        pass
    try:
        return resp["choices"][0]["message"]["content"]
    except Exception:
        try:
            return resp["choices"][0].get("text")
        except Exception:
            return str(resp)

print("Models:")
for i, m in enumerate(models, 1):
    print(f"{i}. {m}")

choice = 0
try:
    choice = int(input(f"Choose model (1-{len(models)}): ")) - 1
    if choice < 0 or choice >= len(models):
        print("Invalid choice, defaulting to 1")
        choice = 0
except Exception:
    print("Invalid input, defaulting to 1")
    choice = 0

selected_model = models[choice]

if not api_key:
    print("Warning: GROQ_API_KEY not set. The client will likely fail until you set it in .env or environment.")

client = Groq(api_key=api_key)

try:
    while True:
        try:
            prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            break

        resp = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": prompt}],
        )
        print("Bot:", extract_reply(resp))
except KeyboardInterrupt:
    print("\nExiting.")