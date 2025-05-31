import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request
import requests
# Загружаем ключ из .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Проверка
if not api_key:
    raise ValueError("API ключ не найден. Убедитесь, что он записан в .env файле")

# Инициализация клиента
client = OpenAI(api_key=api_key)

# Функция анализа тональности
def analyze_sentiment(text):
    response = client.chat.completions.create(
        model="gpt-4",  # можно использовать "gpt-3.5-turbo" если нет доступа к 4
        messages=[
            {"role": "system", "content": "Ты помощник, который определяет тональность текста отзыва клиента. Отвечай одним словом: Позитивный, Нейтральный или Негативный."},
            {"role": "user", "content": f"Отзыв: {text}"}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content.strip()

# Отправка в Telegram
def send_to_telegram(name, phone, feedback, sentiment):
    message = (
        f"📩 *Новый отзыв*\n\n"
        f"👤 Имя: {name}\n"
        f"📱 Номер: {phone}\n"
        f"💬 Отзыв: {feedback}\n"
        f"🧠 Тональность: *{sentiment}*"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

# Страницы Отзыва
@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        feedback = request.form["feedback"]

        sentiment = analyze_sentiment(feedback)
        send_to_telegram(name, phone, feedback, sentiment)

        return thank_you()

    return render_template("form.html")

# Страница крч после отзыва
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)

