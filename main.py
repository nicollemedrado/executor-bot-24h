import os
import requests
import time
import datetime
import threading
from flask import Flask
from tradingview_ta import TA_Handler, Interval, Exchange

# ==================== CONFIGURAÇÕES ====================
TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
CHAT_ID = "-1002692489256"
INTERVALO_ANALISE = 600  # 10 minutos
ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD",
    "EURJPY", "BTCUSD", "ETHUSD"
]

app = Flask(__name__)

# ================ FUNÇÕES AUXILIARES ===================
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def calcular_cliques(rsi):
    if rsi >= 75:
        return 5  # Muito forte
    elif rsi >= 65:
        return 3  # Forte
    elif rsi >= 55:
        return 2  # Moderado
    else:
        return 1  # Fraco ou evitar

def analisar_ativo(simbolo):
    try:
        handler = TA_Handler(
            symbol=simbolo,
            screener="forex",
            exchange="FX_IDC",
            interval=Interval.INTERVAL_5_MINUTES
        )
        analise = handler.get_analysis()
        recomendacao = analise.summary["RECOMMENDATION"]
        rsi = analise.indicators.get("RSI", 50)
        horario = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=2)).strftime("%H:%M")
        cliques = calcular_cliques(rsi)

        direcao = "COMPRA" if recomendacao in ["STRONG_BUY", "BUY"] else "VENDA"
        if cliques > 1:
            dica = f"📌 CLIQUE {cliques}x em {direcao}"
        else:
            dica = "⚠️ CLIQUE APENAS UMA VEZ (sinal fraco)"

        if recomendacao in ["STRONG_BUY", "STRONG_SELL", "BUY", "SELL"]:
            mensagem = f"<b>⚡ SINAL AO VIVO</b>\n\n"
            mensagem += f"🪙 Par: <b>{simbolo}</b>\n"
            mensagem += f"📉 Direção: <b>{direcao}</b>\n"
            mensagem += f"⭐ RSI: {rsi}\n"
            mensagem += f"🕒 Entrada: <b>{horario}</b>\n"
            mensagem += f"⌛ Expiração: 5 minutos\n"
            mensagem += f"{dica}\n\n"
            mensagem += f"<i>Análise com base em TradingView</i>"
            enviar_mensagem(mensagem)
        else:
            enviar_mensagem(f"🔎 {simbolo}: Analisando mercado... Nenhum sinal forte detectado.")

    except Exception as e:
        print(f"Erro em {simbolo}: {e}")

# ================ LOOP PRINCIPAL ===================
def loop_sinais():
    while True:
        for ativo in ATIVOS:
            analisar_ativo(ativo)
            time.sleep(1)
        time.sleep(INTERVALO_ANALISE)

# ================ RENDER FLASK =====================
@app.route("/")
def home():
    return "✅ Executor de Sinais Online"

threading.Thread(target=loop_sinais, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
