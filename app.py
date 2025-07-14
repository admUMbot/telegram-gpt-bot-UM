import os
import time
from flask import Flask, request
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Получаем токены из окружения
TELEGRAM_TOKEN  = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID    = os.getenv("ASSISTANT_ID")

# Проверка на ошибки конфигурации
if not TELEGRAM_TOKEN or not OPENAI_API_KEY or not ASSISTANT_ID:
    raise RuntimeError("Ошибка: проверь TELEGRAM_TOKEN, OPENAI_API_KEY и ASSISTANT_ID в Render → Environment.")

# Инициализация API
client = OpenAI(api_key=OPENAI_API_KEY)
bot    = telegram.Bot(token=TELEGRAM_TOKEN)
app    = Flask(__name__)

# Маршрут для получения апдейтов от Telegram
@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # Проверка на наличие сообщения
    if update.message is None or not update.message.text:
        return "ok"

    chat_id = update.message.chat.id
    user_text = update.message.text.strip()

    try:
        # 1. Создаём новый разговор (thread)
        thread = client.beta.threads.create()

        # 2. Добавляем сообщение пользователя
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_text
        )

        # 3. Запускаем ассистента
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # 4. Ждём завершения run
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status == "completed":
                break
            time.sleep(0.5)

        # 5. Получаем ответ ассистента
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        reply = messages.data[0].content[0].text.value.strip()

        # 6. Отправляем ответ пользователю
        bot.send_message(chat_id=chat_id, text=reply)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text="Произошла ошибка: " + str(e))

    return "ok"

# Простой маршрут для проверки работы
@app.route("/")
def index():
    return "Бот «Ума» запущен 🚀"

# Запуск локального сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
