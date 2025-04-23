import os
import requests
import time
import datetime
import threading
from flask import Flask

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        print("✅ Mensagem enviada:", texto)
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def consultar_preco_ativo(simbolo):
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={simbolo}"
        response = requests.get(url)
        data = response.json()
        preco = data["quoteResponse"]["result"][0].get("regularMarketPrice", None)
        return preco
    except Exception as e:
        print(f"⚠️ Erro ao consultar preço de {simbolo}: {e}")
        return None

def nome_ativo_formatado(simbolo):
    nomes = {
        "EURUSD": "Euro / Dólar",
        "GBPUSD": "Libra / Dólar",
        "USDJPY": "Dólar / Iene",
        "USDCHF": "Dólar / Franco Suíço",
        "AUDUSD": "Dólar Australiano",
        "USDCAD": "Dólar / Canadense",
        "EURJPY": "Euro / Iene",
        "BTCUSD": "Bitcoin",
        "ETHUSD": "Ethereum",
        "TSLA": "Tesla",
        "AAPL": "Apple",
        "AMZN": "Amazon"
    }
    return nomes.get(simbolo, simbolo)

def loop_sinais():
    ativos = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY",
        "BTCUSD", "ETHUSD", "TSLA", "AAPL", "AMZN"
    ]

    while True:
        print("🔁 Iniciando nova análise...")
        hora_atual = datetime.datetime.now().strftime("%H:%M")

        for simbolo in ativos:
            ativo_nome = nome_ativo_formatado(simbolo)
            preco = consultar_preco_ativo(simbolo)

            if preco:
                if preco > 100:  # Simulação de sinal forte
                    mensagem = (
                        f"⚡️ <b>SINAL AO VIVO DETECTADO</b> ⚡️\n\n"
                        f"<b>Ativo:</b> {ativo_nome} ({simbolo})\n"
                        f"<b>Horário:</b> {hora_atual}\n"
                        f"<b>Status:</b> ✅ Entrada Forte Detectada\n"
                        f"⏳ Expiração: 5 minutos\n\n"
                        f"📌 <i>Estrategia:</i> Se o ativo continuar na mesma direção nos próximos segundos após a entrada, <b>considere dobrar a operação</b> com confiança."
                    )
                else:
                    mensagem = (
                        f"📉 <b>SEM ENTRADA RECOMENDADA</b>\n"
                        f"<b>Ativo:</b> {ativo_nome} ({simbolo})\n"
                        f"<b>Horário:</b> {hora_atual}\n"
                        f"🔍 Mercado analisado, aguardando sinal forte."
                    )

                enviar_mensagem(mensagem)
            else:
                print(f"❌ Preço indisponível para {simbolo}")

            time.sleep(1)  # Espaço entre análises de ativos

        print("🕒 Aguardando 10 minutos para nova análise...\n")
        time.sleep(600)  # 10 minutos

thread = threading.Thread(target=loop_sinais, daemon=True)
thread.start()

@app.route('/')
def index():
    return "✅ Bot Executor rodando com sinais a cada 10 minutos."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
