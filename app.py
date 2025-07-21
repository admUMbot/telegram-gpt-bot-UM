from flask import Flask, request, jsonify, send_from_directory
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    
    thread = openai.beta.threads.create()
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    import time
    while True:
        status = openai.beta.threads.runs.retrieve(thread.id, run.id)
        if status.status == "completed":
            break
        elif status.status == "failed":
            return jsonify({"error": "Run failed"}), 500
        time.sleep(1)

    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    reply = messages.data[0].content[0].text.value

    return jsonify({"reply": reply})

@app.route("/", methods=["GET"])
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(port=5000)
