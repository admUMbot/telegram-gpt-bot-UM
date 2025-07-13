import os, time
from flask import Flask, request
from openai import OpenAI               # новый SDK ≥1.0
import telegram
from dotenv import load_dotenv

load_dotenv()

TG_TOKEN   = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ASST_ID    = os.getenv("ASSISTANT_ID")

client = OpenAI(api_key=OPENAI_KEY)
bot    = telegram.Bot(token=TG_TOKEN)
app    = Flask(__name__)

@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(True), bot)
    if update.message is None:
        return "ok"

    chat_id = update.message.chat.id
    user    = update.message.text

    # 1) создаём thread (разговор)
    thread  = client.beta.threads.create()

    # 2) кладём пользовательскую реплику
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user
    )

    # 3) запускаем ассистента «Ума»
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASST_ID
    )

    # 4) ждём, пока run завершится
    while True:
        run = client.beta.threads.runs.retrieve(thread.id, run.id)
        if run.status == "completed":
            break
        time.sleep(0.5)

    # 5) берём последнее сообщение ассистента
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    reply = messages.data[0].content[0].text.value.strip()

    bot.send_message(chat_id, reply)
    return "ok"

@app.route("/")
def index():
    return "Бот «Ума» запущен 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
