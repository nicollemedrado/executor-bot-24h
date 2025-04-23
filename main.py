import os
import requests
import time
import datetime
import threading
from tradingview_ta import TA_Handler, Interval, Exchange

# ============================
# CONFIGURAÇÕES DO BOT
# ============================
TOKEN_TELEGRAM = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TOKEN_TELEGRAM_ID = "-1002692489256"
VALOR_BANCA_INICIAL = 100.0
ENTRADA_PORCENTAGEM = 0.02
INTERVALO_ANALISE = 600  # 10 minutos
STOP_WIN = 0.20  # 20% lucro
STOP_LOSS = 0.10  # 10% prejuízo

banca_atual = VALOR_BANCA_INICIAL
lucro_dia = 0.0
perda_dia = 0.0
ULTIMO_ENVIO = 0

ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD",
    "EURJPY", "NZDUSD", "GBPJPY", "EURGBP", "BTCUSD", "ETHUSD"
]

# ============================
# FUNÇÕES
# ============================
def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {
        "chat_id": TOKEN_TELEGRAM_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
        print("Enviado:", mensagem[:60])
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def analisar_ativo(simbolo):
    handler = TA_Handler(
        symbol=simbolo,
        exchange="OANDA",
        screener="forex",
        interval=Interval.INTERVAL_1_MINUTE
    )
    try:
        analise = handler.get_analysis()
        recomendacao = analise.summary["RECOMMENDATION"]
        rsi = analise.indicators["RSI"]
        return recomendacao, round(rsi, 2)
    except:
        return None, None

def calcular_entrada():
    return round(banca_atual * ENTRADA_PORCENTAGEM, 2)

def gerar_sinal():
    global lucro_dia, perda_dia, banca_atual, ULTIMO_ENVIO
    agora = time.time()

    if agora - ULTIMO_ENVIO < INTERVALO_ANALISE:
        return

    for ativo in ATIVOS:
        direcao, rsi = analisar_ativo(ativo)
        if direcao in ["STRONG_BUY", "STRONG_SELL"]:
            horario = datetime.datetime.now().strftime("%H:%M")
            entrada = calcular_entrada()
            direcao_txt = "COMPRA" if direcao == "STRONG_BUY" else "VENDA"
            cliques = "CLIQUE APENAS UMA VEZ (sinal forte)" if rsi >= 50 else "CLIQUE APENAS UMA VEZ (sinal fraco)"

            mensagem = (
                f"<b>⚡ SINAL AO VIVO</b>\n"
                f"<b>🌐 Par:</b> {ativo}\n"
                f"<b>🔄 Direção:</b> {direcao_txt}\n"
                f"<b>🔢 RSI:</b> {rsi}\n"
                f"<b>💵 Entrada sugerida:</b> R$ {entrada}\n"
                f"<b>⏰ Entrada:</b> {horario}\n"
                f"<b>⏳ Expiração:</b> 5 minutos\n"
                f"⚠ {cliques}\n\n"
                f"<i>Análise com base em TradingView 🔍</i>"
            )
            enviar_telegram(mensagem)
            ULTIMO_ENVIO = agora
            time.sleep(120)
            break
    else:
        enviar_telegram("🔄 Analisando o mercado...")

def loop():
    while True:
        gerar_sinal()
        time.sleep(60)

threading.Thread(target=loop).start()
