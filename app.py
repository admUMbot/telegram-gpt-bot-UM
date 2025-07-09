import os
from flask import Flask, request
import openai
import telegram
from dotenv import load_dotenv

load_dotenv()  # Подтягиваем переменные из .env

TELEGRAM_TOKEN = os.getenv("7598167391:AAFj2Y-TqYXVosHsRUdndL13XCDYZhGsgGo")
OPENAI_API_KEY = os.getenv("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")

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
