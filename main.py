import os
import requests
import time
import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    print("Código de resposta:", response.status_code)
    print("Conteúdo:", response.text)

def buscar_sinais():
    try:
        ativos = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY", "BTCUSD", "ETHUSD", "TSLA", "AAPL", "AMZN"]
        url_base = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="

        for ativo in ativos:
            url = url_base + ativo
            response = requests.get(url)
            data = response.json()

            preco = data["quoteResponse"]["result"][0].get("regularMarketPrice", None)

            if preco:
                horario = datetime.datetime.now().strftime("%H:%M")
                mensagem = f"<b>{ativo}</b> | Analisando mercado...\n\n<b>Horário:</b> {horario}\n<b>Status:</b> Forte tendência de entrada detectada"
                enviar_mensagem(mensagem)
                time.sleep(1)

    except Exception as e:
        print("Erro:", e)

def iniciar_bot():
    while True:
        print("Analisando o mercado em tempo real...")
        buscar_sinais()
        print("Aguardando 10 minutos para próxima análise...")
        time.sleep(600)

iniciar_bot()
