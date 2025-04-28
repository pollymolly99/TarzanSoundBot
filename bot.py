from flask import Flask, request
import requests
import json
import os

TOKEN = os.getenv("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

# Память для звуков
sounds = {}

# Загружаем сохранённые звуки
def load_sounds():
    global sounds
    try:
        with open("sounds.json", "r") as f:
            sounds = json.load(f)
    except FileNotFoundError:
        sounds = {}

# Сохраняем звуки
def save_sounds():
    with open("sounds.json", "w") as f:
        json.dump(sounds, f)

# Отправка голосового сообщения
def send_voice(chat_id, file_id):
    url = URL + "sendVoice"
    data = {"chat_id": chat_id, "voice": file_id}
    requests.post(url, data=data)

# Отправка текстового сообщения
def send_message(chat_id, text):
    url = URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

@app.route('/', methods=['POST'])
def webhook():
    load_sounds()

    update = request.get_json()

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text")
        voice = message.get("voice")
        user_id = message["from"]["id"]
        username = message["from"].get("username", "без_имени")

        if text:
            if text.startswith("/addsound"):
                parts = text.split()
                if len(parts) == 2:
                    sound_name = parts[1]
                    send_message(chat_id, f"Отправь аудио для '{sound_name}'!")
                    sounds[str(user_id)] = sound_name
                    save_sounds()
                else:
                    send_message(chat_id, "Использование: /addsound имя_звука")

            elif text.startswith("/playsound"):
                parts = text.split()
                if len(parts) == 2:
                    sound_name = parts[1]
                    if sound_name in sounds:
                        send_voice(chat_id, sounds[sound_name]["file_id"])
                    else:
                        send_message(chat_id, "Нет такого звука! Используй /listsounds.")
                else:
                    send_message(chat_id, "Использование: /playsound имя_звука")

            elif text.startswith("/listsounds"):
                if sounds:
                    sound_list = "\n".join([f"- {name}" for name in sounds.keys()])
                    send_message(chat_id, f"Доступные звуки:\n{sound_list}")
                else:
                    send_message(chat_id, "Пока нет сохранённых звуков.")

        elif voice:
            if str(user_id) in sounds:
                sound_name = sounds.pop(str(user_id))
                sounds[sound_name] = {
                    "file_id": voice["file_id"],
                    "author": username
                }
                save_sounds()
                send_message(chat_id, f"Звук '{sound_name}' сохранён!")

    return 'ok'

@app.route('/')
def home():
    return 'Bot is running!'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))