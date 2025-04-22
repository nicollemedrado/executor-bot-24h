import requests
import time
from tradingview_ta import TA_Handler, Interval, Exchange
from flask import Flask
import threading
from datetime import datetime, timedelta

# Dados do bot
TELEGRAM_TOKEN = "7214012683:AAG3R6pZzXXeg9Iea3zeDEhw_r2HDG-TY8k"
TELEGRAM_CHAT_ID = "-1002692489256"

# Ativos para monitorar (moedas, ações e cripto suportadas pelo TradingView)
ativos = [
    "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "BTCUSD", "ETHUSD", "AAPL", "TSLA", "AMZN", "MSFT"
]

# Função para analisar e enviar sinal
def verificar_sinais():
    while True:
        sinal_encontrado = False

        for ativo in ativos:
            analise = TA_Handler(
                symbol=ativo,
                screener="crypto" if "USD" in ativo and "BTC" in ativo or "ETH" in ativo else "forex" if "USD" in ativo else "america",
                exchange="BINANCE" if "BTC" in ativo or "ETH" in ativo else "FX_IDC" if "USD" in ativo else "NASDAQ",
                interval=Interval.INTERVAL_5_MINUTES
            )

            try:
                resultado = analise.get_analysis()
                recomendacao = resultado.summary["RECOMMENDATION"]
                estrelas = resultado.summary["BUY"] if recomendacao == "BUY" else resultado.summary["SELL"]

                if recomendacao in ["STRONG_BUY", "STRONG_SELL"]:
                    direcao = "COMPRA" if recomendacao == "STRONG_BUY" else "VENDA"
                    expiracao = "5 minutos"
                    horario_brasil = (datetime.utcnow() - timedelta(hours=3) + timedelta(minutes=2)).strftime("%H:%M")

                    mensagem = f"""⚡ <b>SINAL AO VIVO</b>

🧭 Ativo: <b>{ativo}</b>
📉 Direção: <b>{direcao}</b>
📊 Análise: <b>{recomendacao.replace('_', ' ')}</b>
⏰ Entrar às: <b>{horario_brasil}</b>
⌛ Expiração: <b>{expiracao}</b>
⭐ Força: {'⭐' * int(estrelas)}

<i>Análise baseada no mercado ao vivo via TradingView.</i>"""

                    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                    payload = {
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": mensagem,
                        "parse_mode": "HTML"
                    }

                    requests.post(url, data=payload)
                    print(f"Sinal enviado: {ativo} - {direcao}")
                    sinal_encontrado = True

            except Exception as e:
                print(f"Erro ao analisar {ativo}: {e}")

        if not sinal_encontrado:
            mensagem_neutra = "⚪ <b>Analisando mercado...</b>\n\nNenhum sinal forte encontrado agora. O bot continuará monitorando o TradingView em tempo real."
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": mensagem_neutra,
                "parse_mode": "HTML"
            }
            requests.post(url, data=payload)

        time.sleep(600)  # 10 minutos

# Flask para manter online
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Executor 24h ATIVO!"

def iniciar_bot():
    verificar_sinais()

threading.Thread(target=iniciar_bot).start()

app.run(host="0.0.0.0", port=3000)
