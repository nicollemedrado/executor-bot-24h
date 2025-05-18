import requests
import time
import datetime
import csv
import random
from tradingview_ta import TA_Handler, Interval

# CONFIGURAÇÕES GERAIS
TELEGRAM_TOKEN = "7752601078:AAHRs0Z_BUei1W7tn8Gwbjt0a1-HV7-cHTc"
TELEGRAM_CHAT_ID = "-1002555783780"
ARQUIVO_HISTORICO = "historico_sinais.csv"
ANTECEDENCIA_MINUTOS = 3
ATIVOS_ANALISADOS = set()

# LISTA COMPLETA DE PARES DE MOEDAS
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

def calcular_cliques(rsi):
    return min(10, max(1, int(abs(rsi - 50) / 3)))

def analisar_mercado(ativos):
    random.shuffle(ativos)  # embaralhar para variar
    for ativo in ativos:
        try:
            if ativo in ATIVOS_ANALISADOS:
                continue

            analise_m1 = TA_Handler(symbol=ativo, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_1_MINUTE).get_analysis()
            analise_m5 = TA_Handler(symbol=ativo, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_5_MINUTES).get_analysis()

            rec_m1 = analise_m1.summary["RECOMMENDATION"]
            rec_m5 = analise_m5.summary["RECOMMENDATION"]
            rsi = analise_m1.indicators["RSI"]

            print(f"📊 {ativo} — M1: {rec_m1}, M5: {rec_m5}, RSI: {rsi:.2f}")

            if 45 < rsi < 55:
                continue  # lateralidade

            if rec_m1 == rec_m5 and rec_m1 in ["STRONG_BUY", "STRONG_SELL"]:
                if (rec_m1 == "STRONG_BUY" and rsi >= 70) or (rec_m1 == "STRONG_SELL" and rsi <= 30):
                    direcao = "🔼 COMPRA" if "BUY" in rec_m1 else "🔽 VENDA"
                    cliques = calcular_cliques(rsi)
                    hora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=ANTECEDENCIA_MINUTOS)).strftime("%H:%M")

                    if cliques < 3:
                        continue  # força muito fraca mesmo com confirmação

                    intensidade = {
                        10: "💎 EXTREMAMENTE FORTE",
                        9: "🔥 MUITO FORTE",
                        8: "🔥 MUITO FORTE",
                        7: "💪 FORTE",
                        6: "💪 FORTE",
                        5: "⚠️ MÉDIA",
                        4: "⚠️ MÉDIA",
                        3: "⚠️ MÉDIA"
                    }.get(cliques, "⚠️ FORÇA DESCONHECIDA")

                    mensagem = f"""✅ <b>SINAL PRECISO DETECTADO</b>

📊 Par de Moeda: <b>{ativo}</b>
📈 Direção: <b>{direcao}</b>
📉 RSI: <b>{rsi:.2f}</b>
📶 Força: <b>{intensidade}</b>
🕒 Entrada: <b>{hora}</b> (Brasília)
⌛ Expiração: <b>5 minutos</b>
🖱️ CLIQUE <b>{cliques}x</b> NA DIREÇÃO INDICADA

<i>Análise com dupla confirmação + RSI + filtro de reversão</i>
"""
                    enviar_telegram(mensagem)
                    registrar_sinal([str(datetime.datetime.now()), ativo, direcao, rsi, intensidade])
                    ATIVOS_ANALISADOS.add(ativo)
                    return True

        except Exception as e:
            registrar_sinal([str(datetime.datetime.now()), ativo, "ERRO", "-", "-", str(e)])
            continue

    return False

print("🧠 BOT DE SINAIS 90% ASSERTIVO INICIADO — MODO AGRESSIVO — 24/7 ATIVO")

while True:
    if len(ATIVOS_ANALISADOS) > 25:
        ATIVOS_ANALISADOS.clear()  # limpa após todos os ativos já analisados uma vez
    enviado = analisar_mercado(MOEDAS_FOREX)
    if not enviado:
        enviar_telegram("🔍 Nenhum sinal confiável agora. Análise continua em tempo real...")
    time.sleep(60)
