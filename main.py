import os
import requests
import time
import datetime
import threading
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = "@SalaFantasmaBR"  # Canal fixo

def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    print("Mensagem enviada:", response.text)

def consultar_preco_ativo(simbolo):
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={simbolo}"
        resposta = requests.get(url)
        dados = resposta.json()
        return dados["quoteResponse"]["result"][0].get("regularMarketPrice", None)
    except Exception as erro:
        print(f"Erro ao consultar preço de {simbolo}: {erro}")
        return None

def nome_ativo_formatado(simbolo):
    nomes = {
        "EURUSD": "Euro / Dólar",
        "GBPUSD": "Libra / Dólar",
        "USDJPY": "Dólar / Iene",
        "BTCUSD": "Bitcoin",
        "ETHUSD": "Ethereum",
        "TSLA": "Tesla",
        "AAPL": "Apple",
        "AMZN": "Amazon"
    }
    return nomes.get(simbolo, simbolo)

def loop_sinais():
    # Mensagem inicial
    mensagem_inicial = (
        "🤖 <b>BOT EXECUTOR INICIADO COM SUCESSO!</b>\n\n"
        "⏰ Aguardando sinais ao vivo...\n"
        "📡 O sistema está analisando o mercado 24h por dia."
    )
    enviar_mensagem(mensagem_inicial)

    ativos = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD", "TSLA", "AAPL", "AMZN"]

    while True:
        print("⏳ Iniciando análise dos ativos...")

        for simbolo in ativos:
            preco = consultar_preco_ativo(simbolo)
            if preco:
                nome = nome_ativo_formatado(simbolo)
                hora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M")

                if preco > 100:  # Simulação de entrada forte
                    mensagem = (
                        f"⚡ <b>SINAL AO VIVO DETECTADO</b> ⚡\n"
                        f"<b>Ativo:</b> {nome} ({simbolo})\n"
                        f"<b>Horário:</b> {hora}\n"
                        f"<b>Status:</b> ✅ Entrada Forte Detectada\n"
                        f"☑️ <i>Prepare-se para operar!</i>"
                    )
                else:
                    mensagem = (
                        f"📉 <b>SEM ENTRADA RECOMENDADA</b>\n"
                        f"<b>Ativo:</b> {nome} ({simbolo})\n"
                        f"<b>Horário:</b> {hora}\n"
                        f"🔍 Mercado analisado, aguardando movimento forte."
                    )

                enviar_mensagem(mensagem)
                time.sleep(1)

        print("🔁 Aguardando 10 minutos para a próxima análise...")
        time.sleep(600)

@app.route('/')
def index():
    return "✅ Bot Executor está rodando com análise de sinais 24h."

threading.Thread(target=loop_sinais, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
