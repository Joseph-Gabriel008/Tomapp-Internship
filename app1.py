from flask import Flask, request
import requests

app = Flask(__name__)

# ===============================
# 🔐 CONFIGURATION
# ===============================
BOT_TOKEN = "Enter your bot token"
OPENROUTER_API_KEY = "Enter Your bot Token"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "openai/gpt-4o-mini"

# ===============================
# 🧠 LLM FUNCTION
# ===============================
def ask_ai(prompt):
    try:
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an academic assistant. "
                        "Understand the user's intent and explain clearly in simple language."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Academic Telegram Bot"
        }

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=20
        )

        if response.status_code != 200:
            print("OPENROUTER ERROR:", response.text)
            return "⚠️ AI is currently unavailable. Please try again."

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ AI is busy right now. Please try again."

# ===============================
# 🔌 EXTERNAL API FUNCTION (JOKE API)
# ===============================
def get_joke():
    try:
        res = requests.get(
            "https://official-joke-api.appspot.com/random_joke",
            timeout=10
        )
        data = res.json()
        return f"😂 {data['setup']}\n\n👉 {data['punchline']}"
    except Exception as e:
        print("JOKE API ERROR:", e)
        return "⚠️ Could not fetch a joke right now."

# ===============================
# 📩 TELEGRAM WEBHOOK
# ===============================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    if "message" not in data:
        return "OK"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if not text:
        send_message(chat_id, "❗ Please send a text message.")
        return "OK"

    if text.startswith("/start"):
        send_message(
            chat_id,
            "👋 Hello!\n"
            "I am an Academic Assistant Bot.\n\n"
            "Commands:\n"
            "• get joke\n"
            "• ask any academic question"
        )
        return "OK"

    # 🔑 Intent-based routing
    if text.lower() in ["get joke", "joke", "tell me a joke"]:
        reply = get_joke()
    else:
        reply = ask_ai(text)

    send_message(chat_id, reply)
    return "OK"

# ===============================
# 📤 SEND MESSAGE TO TELEGRAM
# ===============================
def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

# ===============================
# 🚀 RUN SERVER
# ===============================
if __name__ == "__main__":
    app.run(port=5000)
