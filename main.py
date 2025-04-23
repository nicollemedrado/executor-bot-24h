import os
import requests
import time
import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# =========================
# CONFIGURAÇÕES DO SISTEMA
# =========================
ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY",
    "BTCUSD", "ETHUSD"
]
VALOR_BANCA_INICIAL = 100.0
ENTRADA_PORCENTAGEM = 0.02
STOP_WIN = 0.10
STOP_LOSS = 0.05
INTERVALO_ANALISE = 600  # 10 minutos

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

banca_atual = VALOR_BANCA_INICIAL
lucro_dia = 0.0
perda_dia = 0.0

# =========================
# FUNÇÕES DO BOT
# =========================
def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def analisar_mercado(simbolo):
    handler = TA_Handler(
        symbol=simbolo,
        exchange="FX_IDC" if simbolo not in ["BTCUSD", "ETHUSD"] else "BINANCE",
        screener="crypto" if simbolo in ["BTCUSD", "ETHUSD"] else "forex",
        interval=Interval.INTERVAL_5_MINUTES
    )
    try:
        analise = handler.get_analysis()
        recomendacao = analise.summary["RECOMMENDATION"]
        return recomendacao
    except Exception as e:
        print(f"Erro ao analisar {simbolo}:", e)
        return None

def simular_analise(simbolo):
    global banca_atual, lucro_dia, perda_dia
    agora = datetime.datetime.now().strftime("%H:%M")
    recomendacao = analisar_mercado(simbolo)

    if not recomendacao:
        return False

    if recomendacao not in ["STRONG_BUY", "STRONG_SELL"]:
        return False

    direcao = "COMPRA" if recomendacao == "STRONG_BUY" else "VENDA"
    entrada = round(banca_atual * ENTRADA_PORCENTAGEM, 2)
    dica_dobra = "\n📌 <b>DICA:</b> Se o ativo continuar na mesma direção, dobre a operação após 1 minuto."

    if lucro_dia >= STOP_WIN * VALOR_BANCA_INICIAL:
        enviar_mensagem("✅ <b>Meta de lucro atingida.</b> Parando operações do dia.")
        return False
    if perda_dia >= STOP_LOSS * VALOR_BANCA_INICIAL:
        enviar_mensagem("⚠️ <b>Limite de perda atingido.</b> Parando operações do dia.")
        return False

    mensagem = (
        f"⚡ <b>SINAL AO VIVO</b>\n\n"
        f"💹 Ativo: <b>{simbolo}</b>\n"
        f"⏰ Horário: <b>{agora}</b>\n"
        f"🎯 Direção: <b>{direcao}</b>\n"
        f"💰 Entrada sugerida: R$ {entrada}\n"
        f"⌛ Expiração: 5 minutos"
        f"{dica_dobra}\n\n"
        f"<i>Baseado em análise real via TradingView.</i>"
    )
    enviar_mensagem(mensagem)
    lucro_dia += entrada * 0.85  # simula lucro
    return True

# =========================
# LOOP PRINCIPAL
# =========================
def iniciar_bot():
    while True:
        print("🔎 Analisando mercado...")
        sinal_detectado = False
        for ativo in ATIVOS:
            if simular_analise(ativo):
                sinal_detectado = True
                time.sleep(2)  # intervalo entre sinais
        if not sinal_detectado:
            enviar_mensagem("🕵️ Nenhum sinal forte detectado. O sistema segue monitorando...")
        print("⏳ Aguardando próxima análise...")
        time.sleep(INTERVALO_ANALISE)

if __name__ == "__main__":
    iniciar_bot()
