import os
import requests
import time
import datetime
from flask import Flask
import threading
from tradingview_ta import TA_Handler, Interval, Exchange

# Configurações de autenticação do Telegram
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

# Lista completa de ativos disponíveis na plataforma
ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY",
    "BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD", "TSLA", "AAPL", "AMZN",
    "NZDUSD", "EURGBP", "EURAUD", "EURCAD", "AUDCAD", "CADCHF",
    "CHFJPY", "GBPJPY", "GBPCAD", "NZDJPY"
]

INTERVALO_ANALISE = 120  # A cada 2 minutos
EXPIRACAO = "2 minutos"  # Tempo da operação

app = Flask(__name__)

# Função para enviar mensagens no Telegram
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
        print("✅ Mensagem enviada")
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

# Função principal de análise e envio de sinais
def analisar_e_enviar():
    sinal_encontrado = False

    for ativo in ATIVOS:
        try:
            analise = TA_Handler(
                symbol=ativo,
                screener="forex",
                exchange="FX_IDC",
                interval=Interval.INTERVAL_1_MINUTE
            ).get_analysis()

            recomendacao = analise.summary["RECOMMENDATION"]
            rsi = analise.indicators.get("RSI", 0)
            agora = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
            horario = (agora + datetime.timedelta(minutes=2)).strftime("%H:%M")
            entrada = 2.00

            if recomendacao in ["STRONG_BUY", "STRONG_SELL"]:
                direcao = "COMPRA" if recomendacao == "STRONG_BUY" else "VENDA"
                mensagem = (
                    f"⚡ <b>SINAL AO VIVO</b>\n"
                    f"🌐 Par: <b>{ativo}</b>\n"
                    f"🔄 Direção: <b>{direcao}</b>\n"
                    f"🔢 RSI: <b>{rsi:.2f}</b>\n"
                    f"💵 Entrada sugerida: R$ {entrada}\n"
                    f"⏰ Entrada: <b>{horario}</b>\n"
                    f"⏳ Expiração: {EXPIRACAO}\n"
                    f"⚠ CLIQUE APENAS UMA VEZ (sinal forte)\n"
                )
                enviar_mensagem(mensagem)
                sinal_encontrado = True
        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")

    if not sinal_encontrado:
        mensagem = (
            "🔍 <b>Analisando mercado...</b>\n"
            "<i>Nenhum sinal forte detectado por enquanto. O bot continua monitorando.</i>"
        )
        enviar_mensagem(mensagem)

# Loop contínuo de execução
def iniciar_bot():
    while True:
        print("🔄 Executando análise de mercado...")
        analisar_e_enviar()
        time.sleep(INTERVALO_ANALISE)

@app.route("/")
def home():
    return "✅ Bot Executor 24h Rodando"

threading.Thread(target=iniciar_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
