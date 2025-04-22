import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def descobrir_chat_id():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    response = requests.get(url)
    print(response.json())

descobrir_chat_id()
