import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing")

models = ["llama-3.3-70b-versatile", "qwen/qwen3-32b"]

print("Models:")
for i, m in enumerate(models, 1):
    print(f"{i}. {m}")

choice = int(input("Choose model (1-2): ")) - 1
selected_model = models[choice]

client = Groq(api_key=api_key)

while True:
    prompt = input("You: ").strip()
    if prompt.lower() in {"exit", "quit"}:
        break

    resp = client.chat.completions.create(
        model=selected_model,
        messages=[{"role": "user", "content": prompt}],
    )
    print("Bot:", resp.choices[0].message.content)