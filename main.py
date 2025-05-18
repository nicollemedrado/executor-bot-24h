import requests
import time
import datetime
import csv
from tradingview_ta import TA_Handler, Interval

# CONFIGURAÇÕES
TELEGRAM_TOKEN = "8114639244:AAFHL2WS5RAwgoxMr2VRZ00LtzAbCoKlCFY"
TELEGRAM_CHAT_ID = "-1002555783780"
ARQUIVO_HISTORICO = "historico_sinais.csv"

ATIVOS = [
    "EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCHF", "EURJPY", "GBPJPY"
]

def enviar_telegram(mensagem):
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

def registrar_sinal(dados):
    with open(ARQUIVO_HISTORICO, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(dados)

def analisar_e_enviar():
    encontrou = False

    for ativo in ATIVOS:
        try:
            analise_m1 = TA_Handler(symbol=ativo, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_1_MINUTE).get_analysis()
            analise_m5 = TA_Handler(symbol=ativo, screener="forex", exchange="FX_IDC", interval=Interval.INTERVAL_5_MINUTES).get_analysis()
            rec_m1 = analise_m1.summary["RECOMMENDATION"]
            rec_m5 = analise_m5.summary["RECOMMENDATION"]
            rsi = analise_m1.indicators["RSI"]

            # Mercado lateral? Ignora
            if 45 < rsi < 55:
                enviar_telegram(f"⚠️ <b>{ativo}</b> ignorado — mercado lateral (RSI {rsi:.2f})")
                registrar_sinal([str(datetime.datetime.now()), ativo, "IGNORADO", rsi, "LATERAL", "-"])
                continue

            # Confirmar tendência com força dupla
            if rec_m1 == rec_m5 and rec_m1 in ["STRONG_BUY", "STRONG_SELL"]:
                direcao = "🔼 COMPRA" if "BUY" in rec_m1 else "🔽 VENDA"

                # Força do sinal (RSI)
                if rsi >= 90 or rsi <= 10:
                    intensidade = "💎 EXTREMAMENTE FORTE"
                    cliques = 10
                elif rsi >= 80 or rsi <= 20:
                    intensidade = "🔥 MUITO FORTE"
                    cliques = 7
                elif rsi >= 70 or rsi <= 30:
                    intensidade = "💪 FORTE"
                    cliques = 5
                elif rsi >= 65 or rsi <= 35:
                    intensidade = "⚠️ MÉDIA"
                    cliques = 3
                else:
                    continue

                hora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=3)).strftime("%H:%M")

                mensagem = f"""✅ <b>SINAL CONFIRMADO</b>

🪙 Par: <b>{ativo}</b>
📈 Direção: <b>{direcao}</b>
📊 RSI atual: <b>{rsi:.2f}</b>
📶 Força do Sinal: <b>{intensidade}</b>
🕒 Entrada: <b>{hora}</b> (Brasília)
⏳ Expiração: <b>5 minutos</b>
🖱️ Clique <b>{cliques}x</b> na direção indicada

<i>Sinal gerado por análise M1+M5 com validação RSI</i>"""
                enviar_telegram(mensagem)
                registrar_sinal([str(datetime.datetime.now()), ativo, direcao, rsi, intensidade, "ENVIADO"])
                encontrou = True
                break
        except Exception as e:
            enviar_telegram(f"⚠️ Erro ao analisar {ativo}: {e}")
            registrar_sinal([str(datetime.datetime.now()), ativo, "ERRO", "-", "-", str(e)])

    if not encontrou:
        enviar_telegram("🔍 Nenhum sinal forte identificado no momento. Análise em andamento...")
        registrar_sinal([str(datetime.datetime.now()), "-", "-", "-", "-", "SEM SINAL"])

# LOOP contínuo de segunda a sexta, das 09h às 18h
while True:
    agora = datetime.datetime.now()
    if agora.weekday() < 5 and 9 <= agora.hour < 18:
        analisar_e_enviar()
    time.sleep(120)
