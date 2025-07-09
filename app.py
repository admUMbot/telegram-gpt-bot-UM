from flask import Flask, request
import openai
import telegram

# Настройки
app = Flask(__name__)
TELEGRAM_TOKEN = '7598167391:AAFj2Y-TqYXVosHsRUdndL13XCDYZhGsgGo'
OPENAI_API_KEY = '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'
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Устанавливаем ключ API OpenAI
openai.api_key = OPENAI_API_KEY

# Обработка входящих сообщений от Telegram
@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    user_text = update.message.text

    # Отправка текста в OpenAI (ChatGPT)
    response = openai.ChatCompletion.create(
        model="gpt-4",  # или "gpt-3.5-turbo", если нет GPT-4
        messages=[{"role": "user", "content": user_text}]
    )

    reply = response['choices'][0]['message']['content']
    bot.send_message(chat_id=chat_id, text=reply)
    return 'ok'
