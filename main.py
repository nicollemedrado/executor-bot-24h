
import requests
import time
import datetime
import csv
import random
from tradingview_ta import TA_Handler, Interval

# CONFIGURAÇÕES
TELEGRAM_TOKEN = "7752601078:AAHRs0Z_BUei1W7tn8Gwbjt0a1-HV7-cHTc"
TELEGRAM_CHAT_ID = "-1002555783780"
ARQUIVO_HISTORICO = "historico_sinais.csv"
ANTECEDENCIA_MINUTOS = 3
HISTORICO_ATIVOS = {}

# PARES DE MOEDAS (FOREX)
MOEDAS_FOREX = [
    "EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCHF", "USDCAD",
    "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY", "EURAUD", "EURGBP",
    "GBPAUD", "NZDJPY", "AUDNZD", "USDHKD", "USDZAR", "USDMXN", "EURCAD",
    "EURCHF", "AUDCAD", "NZDCAD", "NZDCHF", "CADCHF", "GBPCAD"
]

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def registrar_sinal(dados):
    with open(ARQUIVO_HISTORICO, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(dados)

def classificar_forca(rsi):
    if rsi >= 90 or rsi <= 10:
        return "💎 EXTREMAMENTE FORTE", 10
    elif rsi >= 80 or rsi <= 20:
        return "🔥 MUITO FORTE", 7
    elif rsi >= 70 or rsi <= 30:
        return "💪 FORTE", 5
    elif rsi >= 65 or rsi <= 35:
        return "⚠️ MODERADA", 3
    else:
        return None, 0

def analisar_todos_os_ativos(ativos):
    random.shuffle(ativos)
    sinais_enviados = 0
    agora = datetime.datetime.now()

    for ativo in ativos:
        try:
            ultima_entrada = HISTORICO_ATIVOS.get(ativo)
            if ultima_entrada and (agora - ultima_entrada).total_seconds() < 900:
                continue  # ignora ativo analisado nos últimos 15 minutos

            analise_m1 = TA_Handler(symbol=ativo, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_1_MINUTE).get_analysis()
            analise_m5 = TA_Handler(symbol=ativo, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_5_MINUTES).get_analysis()
            rec_m1 = analise_m1.summary["RECOMMENDATION"]
            rec_m5 = analise_m5.summary["RECOMMENDATION"]
            rsi = analise_m1.indicators["RSI"]

            print(f"📊 {ativo} — M1: {rec_m1}, M5: {rec_m5}, RSI: {rsi:.2f}")

            if rec_m1 == rec_m5 and rec_m1 in ["STRONG_BUY", "STRONG_SELL"]:
                intensidade, cliques = classificar_forca(rsi)
                if not intensidade or cliques < 3:
                    continue

                direcao = "🔼 COMPRA" if "BUY" in rec_m1 else "🔽 VENDA"
                hora = (agora - datetime.timedelta(hours=3) + datetime.timedelta(minutes=ANTECEDENCIA_MINUTOS)).strftime("%H:%M")

                mensagem = f"""✅ <b>SINAL REAL DETECTADO</b>

📊 Par de Moeda: <b>{ativo}</b>
📈 Direção: <b>{direcao}</b>
📉 RSI: <b>{rsi:.2f}</b>
📶 Força: <b>{intensidade}</b>
🕒 Entrada: <b>{hora}</b> (Brasília)
⌛ Expiração: <b>5 minutos</b>
🖱️ CLIQUE <b>{cliques}x</b> NA DIREÇÃO INDICADA

<i>Confirmação dupla (M1/M5) + RSI filtrado — assertividade máxima</i>
"""
                enviar_telegram(mensagem)
                registrar_sinal([str(datetime.datetime.now()), ativo, direcao, rsi, intensidade])
                HISTORICO_ATIVOS[ativo] = agora
                sinais_enviados += 1

        except Exception as e:
            registrar_sinal([str(datetime.datetime.now()), ativo, "ERRO", "-", "-", str(e)])
            continue

    return sinais_enviados

print("📡 BOT AGRESSIVO ATIVO — ESCANEANDO TODOS OS PARES EM BUSCA DE SINAIS REAIS — 24H")

while True:
    sinais = analisar_todos_os_ativos(MOEDAS_FOREX)
    if sinais == 0:
        enviar_telegram("🚫 Nenhum sinal confirmado neste momento. Mercado monitorado em tempo real.")
    time.sleep(60)
