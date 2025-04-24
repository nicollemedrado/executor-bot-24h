import os
import requests
import time
import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# ========== CONFIGURAÇÕES ==========
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY",
    "NZDUSD", "EURGBP", "CHFJPY", "GBPJPY", "CADJPY", "EURAUD",
    "BTCUSD", "ETHUSD"
]

VALOR_BANCA = 100
PORCENTAGEM_ENTRADA = 0.02  # 2% da banca
INTERVALO_ANALISE = 600  # 10 minutos

STOP_WIN = 0.10  # 10% da banca
STOP_LOSS = 0.05  # 5% da banca

lucro_total = 0
perda_total = 0

# ========== FUNÇÕES ==========
def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def obter_rsi(par):
    try:
        analise = TA_Handler(
            symbol=par,
            screener="forex",
            exchange="FX_IDC",
            interval=Interval.INTERVAL_5_MINUTES
        )
        resultado = analise.get_analysis()
        rsi = resultado.indicators["RSI"]
        return rsi
    except:
        return None

def gerar_sinal(par):
    global lucro_total, perda_total

    rsi = obter_rsi(par)
    if rsi is None:
        return

    agora = datetime.datetime.now() - datetime.timedelta(hours=3)  # horário BR
    horario_entrada = (agora + datetime.timedelta(minutes=2)).strftime("%H:%M")
    direcao = "COMPRA" if rsi < 30 else "VENDA" if rsi > 70 else None
    entrada = round(VALOR_BANCA * PORCENTAGEM_ENTRADA, 2)

    if lucro_total >= VALOR_BANCA * STOP_WIN:
        enviar_telegram("🟢 <b>Meta de lucro atingida. Operações pausadas.</b>")
        return
    elif perda_total >= VALOR_BANCA * STOP_LOSS:
        enviar_telegram("🔴 <b>Limite de perda atingido. Operações pausadas.</b>")
        return

    if direcao:
        intensidade = "⚠ CLIQUE APENAS UMA VEZ (sinal forte)" if (rsi < 25 or rsi > 75) else "⚠ Entrada opcional (sinal fraco)"
        mensagem = (
            f"⚡ <b>SINAL AO VIVO</b>\n"
            f"🌐 Par: {par}\n"
            f"🔄 Direção: {direcao}\n"
            f"🔢 RSI: {round(rsi, 2)}\n"
            f"💵 Entrada sugerida: R$ {entrada}\n"
            f"⏰ Entrada: {horario_entrada}\n"
            f"⏳ Expiração: 5 minutos\n"
            f"{intensidade}"
        )
        enviar_telegram(mensagem)
    else:
        enviar_telegram(f"🕵️ Analisando {par} - Nenhuma entrada detectada. RSI: {round(rsi, 2)}")

# ========== LOOP PRINCIPAL ==========
while True:
    print("⏳ Iniciando análise de mercado...")
    for ativo in ATIVOS:
        gerar_sinal(ativo)
        time.sleep(2)
    print("🕒 Aguardando próximo ciclo...")
    time.sleep(INTERVALO_ANALISE)
