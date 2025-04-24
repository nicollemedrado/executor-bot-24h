import os
import requests
import time
from tradingview_ta import TA_Handler, Interval, Exchange
from datetime import datetime, timedelta
from flask import Flask
import threading

# ================== CONFIGURAÇÕES ======================
TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
CHAT_ID = "-1002692489256"
INTERVALO_ENVIO = 180  # Enviar sinais a cada 3 minutos
EXPIRACAO = "2 minutos"  # Tempo da operação

ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY",
    "NZDUSD", "GBPJPY", "CADJPY", "CHFJPY", "EURGBP", "EURAUD", "GBPCAD",
    "BTCUSD", "ETHUSD"
]

app = Flask(__name__)

# ============== FUNÇÕES PRINCIPAIS ======================
def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
        print("Mensagem enviada com sucesso!")
    except:
        print("Erro ao enviar mensagem para o Telegram.")


def analisar_mercado():
    sinais_enviados = 0
    for ativo in ATIVOS:
        try:
            analise = TA_Handler(
                symbol=ativo,
                screener="forex",
                exchange="FX_IDC",
                interval=Interval.INTERVAL_1_MINUTE
            )
            resultado = analise.get_analysis()
            rsi = resultado.indicators.get("RSI", None)
            direcao = resultado.summary["RECOMMENDATION"]
            agora = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M")

            if direcao in ["STRONG_BUY", "STRONG_SELL"]:
                direcao_texto = "COMPRA" if direcao == "STRONG_BUY" else "VENDA"

                # Decidir se recomenda clicar mais de uma vez
                cliques = "1 VEZ" if rsi < 70 and rsi > 30 else (
                    "2 VEZES" if rsi <= 30 or rsi >= 70 else "1 VEZ"
                )

                mensagem = f"""⚡ <b>SINAL AO VIVO</b>
🌐 Par: <b>{ativo}</b>
↺ Direção: <b>{direcao_texto}</b>
🔢 RSI: <b>{round(rsi, 2)}</b>
💵 Entrada sugerida: <b>R$ 2.0</b>
⏰ Entrada: <b>{agora}</b>
⏳ Expiração: <b>{EXPIRACAO}</b>
⚠ CLIQUE: <b>{cliques}</b>

<i>Baseado em análise ao vivo do mercado via TradingView.</i>
"""
                enviar_mensagem(mensagem)
                sinais_enviados += 1

        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")

    if sinais_enviados == 0:
        enviar_mensagem("<b>⌛ Analisando mercado...</b>\n\nNenhum sinal forte detectado no momento. Aguarde o próximo ciclo.")


# ================== EXECUÇÃO CONTÍNUA ======================
def loop_bot():
    while True:
        print("Analisando mercado ao vivo...")
        analisar_mercado()
        print(f"Aguardando {INTERVALO_ENVIO // 60} minutos para nova análise...")
        time.sleep(INTERVALO_ENVIO)


@app.route("/")
def home():
    return "🚀 Bot Executor ativo com RSI e recomendação inteligente!"

if __name__ == '__main__':
    threading.Thread(target=loop_bot).start()
    app.run(host='0.0.0.0', port=10000)
