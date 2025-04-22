import requests
import time
from tradingview_ta import TA_Handler, Interval, Exchange
from flask import Flask
import threading
from datetime import datetime, timedelta
import os

# Variáveis de ambiente (você configurou no Render)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Pares para monitorar (inclui moedas, ações e criptos mais populares)
pares = [
    "EURUSD", "USDJPY", "AUDUSD", "GBPUSD",  # Moedas
    "BTCUSD", "ETHUSD", "SOLUSD",            # Criptomoedas
    "AAPL", "TSLA", "MSFT", "NVDA"           # Ações populares (na corretora Pocket Option pode ter variantes)
]

# Função para verificar e enviar os sinais
def verificar_sinais():
    while True:
        sinal_encontrado = False

        for par in pares:
            try:
                analise = TA_Handler(
                    symbol=par,
                    screener="crypto" if "USD" in par and par not in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"] else "forex",
                    exchange="BINANCE" if "USD" in par and par not in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"] else "FX_IDC",
                    interval=Interval.INTERVAL_5_MINUTES
                )

                resultado = analise.get_analysis()
                recomendacao = resultado.summary["RECOMMENDATION"]
                estrelas = resultado.summary["BUY"] if recomendacao == "BUY" else resultado.summary["SELL"]

                if recomendacao in ["STRONG_BUY", "STRONG_SELL"]:
                    direcao = "COMPRA" if recomendacao == "STRONG_BUY" else "VENDA"
                    expiracao = "5 minutos"
                    horario_brasil = (datetime.utcnow() - timedelta(hours=3) + timedelta(minutes=2)).strftime("%H:%M")

                    mensagem = f"""⚡ <b>SINAL AO VIVO</b>

🧭 Par: <b>{par}</b>
📉 Direção: <b>{direcao}</b>
📊 Análise: <b>{recomendacao.replace('_', ' ')}</b>
⏰ Entrar às: <b>{horario_brasil}</b>
⌛ Expiração: <b>{expiracao}</b>
⭐ Força: {'⭐' * int(estrelas)}

<i>Baseado em análise ao vivo do mercado via TradingView.</i>"""

                    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                    payload = {
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": mensagem,
                        "parse_mode": "HTML"
                    }

                    response = requests.post(url, data=payload)
                    print(f"Sinal enviado: {par} - {direcao}")
                    sinal_encontrado = True

            except Exception as e:
                print(f"Erro ao analisar {par}: {e}")

        if not sinal_encontrado:
            mensagem_neutra = "⚪ <b>Analisando mercado...</b>\n\nNenhum sinal forte encontrado nesse momento. O bot continuará monitorando o TradingView em tempo real."
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": mensagem_neutra,
                "parse_mode": "HTML"
            }
            requests.post(url, data=payload)

        time.sleep(600)  # Verifica a cada 10 minutos

# Inicia o servidor Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Executor 24h ATIVO! 🟢"

# Thread para rodar a verificação dos sinais
def iniciar_bot():
    verificar_sinais()

threading.Thread(target=iniciar_bot).start()

# Executa o servidor (adaptado para Render.com com PORT dinâmico)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
