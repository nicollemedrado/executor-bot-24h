import os
import time
import datetime
import requests
from tradingview_ta import TA_Handler, Interval, Exchange

TOKEN = os.getenv("7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68")
CHAT_ID = os.getenv("-1002692489256")

# Configurações da banca
BANCA_INICIAL = 100.0
ENTRADA_PORCENTAGEM = 0.02
STOP_WIN = 0.10
STOP_LOSS = 0.05
INTERVALO_ANALISE = 600  # 10 minutos

banca_atual = BANCA_INICIAL
lucro_dia = 0.0
perda_dia = 0.0

ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY",
    "NZDUSD", "NZDJPY", "GBPJPY", "EURGBP"
]

def enviar_mensagem(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def analisar_ativo(simbolo):
    handler = TA_Handler(
        symbol=simbolo,
        screener="forex",
        exchange="FX_IDC",
        interval=Interval.INTERVAL_1_MINUTE
    )

    try:
        analise = handler.get_analysis()
        rsi = analise.indicators['RSI']
        recomendacao = analise.summary['RECOMMENDATION']
        return rsi, recomendacao
    except:
        return None, None

def gerar_sinal(simbolo):
    global banca_atual, lucro_dia, perda_dia

    rsi, recomendacao = analisar_ativo(simbolo)
    agora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%H:%M")
    entrada_valor = round(banca_atual * ENTRADA_PORCENTAGEM, 2)

    if lucro_dia >= BANCA_INICIAL * STOP_WIN:
        enviar_mensagem("🎯 <b>Meta diária atingida!</b>\nBot pausado para preservar lucros.")
        return False
    if perda_dia >= BANCA_INICIAL * STOP_LOSS:
        enviar_mensagem("⛔ <b>Limite de perda atingido!</b>\nBot pausado para proteção.")
        return False

    if recomendacao in ["STRONG_BUY", "STRONG_SELL"]:
        direcao = "COMPRA" if recomendacao == "STRONG_BUY" else "VENDA"
        dica = "⚠ CLIQUE APENAS UMA VEZ (sinal forte)"
    elif recomendacao in ["BUY", "SELL"]:
        direcao = "COMPRA" if recomendacao == "BUY" else "VENDA"
        dica = "⚠ CLIQUE APENAS UMA VEZ (sinal fraco)"
    else:
        return True

    mensagem = (
        f"⚡ <b>SINAL AO VIVO</b>\n"
        f"🌐 Par: <b>{simbolo}</b>\n"
        f"🔄 Direção: <b>{direcao}</b>\n"
        f"🔢 RSI: <b>{round(rsi, 2)}</b>\n"
        f"💵 Entrada sugerida: R$ {entrada_valor}\n"
        f"⏰ Entrada: <b>{agora}</b>\n"
        f"⏳ Expiração: 5 minutos\n"
        f"{dica}\n\n"
        f"<i>Análise com base em TradingView</i>"
    )

    enviar_mensagem(mensagem)
    return True

def executar_bot():
    while True:
        enviar_mensagem("📡 <b>Analisando o mercado ao vivo...</b>")
        for ativo in ATIVOS:
            resultado = gerar_sinal(ativo)
            if not resultado:
                return
            time.sleep(2)
        time.sleep(INTERVALO_ANALISE)

if __name__ == "__main__":
    executar_bot()
