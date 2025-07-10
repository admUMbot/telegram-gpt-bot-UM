import os
from flask import Flask, request
import openai
import telegram
from dotenv import load_dotenv

load_dotenv()  # Подтягиваем переменные из .env

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
bot = telegram.Bot(token=TELEGRAM_TOKEN)

app = Flask(__name__)

@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    user_text = update.message.text or ""

    # Запрос к ChatGPT
    completion = openai.ChatCompletion.create(
        model="gpt-4o",          # можно gpt-3.5-turbo
        messages=[{"role": "user", "content": user_text}],
        temperature=0.7
    )

    reply = completion.choices[0].message.content.strip()
    bot.send_message(chat_id=chat_id, text=reply)
    return "ok"

if __name__ == "__main__":
    # Локальный запуск
    app.run(host="0.0.0.0", port=5000, debug=True)
