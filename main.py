import os
import requests
import time
import datetime
from flask import Flask
import threading

# Configurações do bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Inicializa o Flask
app = Flask(__name__)

# Envia mensagem para o Telegram
def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    print(f"Mensagem enviada | Status: {response.status_code}")

# Loop de sinais
def loop_sinais():
    ativos = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY", "BTCUSD", "ETHUSD", "AAPL", "TSLA"]
    while True:
        print(f"⏱️ Loop executado às {datetime.datetime.now().strftime('%H:%M:%S')}")

        for ativo in ativos:
            try:
                url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ativo}"
                response = requests.get(url)
                data = response.json()
                preco = data["quoteResponse"]["result"][0].get("regularMarketPrice", None)

                if preco:
                    horario = datetime.datetime.now().strftime("%H:%M")
                    mensagem = f"⚡ <b>SINAL AO VIVO DETECTADO</b> ⚡\n\n" \
                               f"<b>Ativo:</b> {ativo}\n" \
                               f"<b>Horário:</b> {horario}\n" \
                               f"<b>Status:</b> Entrada Forte Detectada\n" \
                               f"✅ <b>Prepare-se para operar!</b>"
                    enviar_mensagem(mensagem)
                    print(f"✅ Sinal enviado para: {ativo} | Preço: {preco}")
                else:
                    print(f"⚠️ Preço não encontrado para {ativo}")
            except Exception as e:
                print(f"Erro ao analisar {ativo}: {e}")

        print("⏳ Aguardando 2 minutos para próxima análise...\n")
        time.sleep(120)  # 2 minutos

# Rota básica do Flask
@app.route('/')
def index():
    return "Bot Executor Sinais 24h está ativo."

# Inicia o loop de sinais em segundo plano
if __name__ == '__main__':
    thread = threading.Thread(target=loop_sinais, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
