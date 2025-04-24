import os
import requests
import time
from datetime import datetime, timedelta
from tradingview_ta import TA_Handler, Interval, Exchange

# Tokens do Telegram
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

# Lista completa de ativos disponíveis na Pocket Option
ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY",
    "NZDUSD", "EURGBP", "EURCHF", "GBPJPY", "CHFJPY", "NZDJPY", "GBPCAD",
    "BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "TSLA", "AAPL", "AMZN"
]

# Função para enviar mensagens para o Telegram
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
        print(f"Erro ao enviar mensagem: {e}")

# Função para obter o horário atual no Brasil
def horario_brasil():
    return (datetime.utcnow() - timedelta(hours=3)).strftime('%H:%M')

# Função para determinar quantidade de cliques com base no RSI
def calcular_cliques(rsi):
    if rsi >= 90 or rsi <= 10:
        return 10
    elif rsi >= 85 or rsi <= 15:
        return 8
    elif rsi >= 80 or rsi <= 20:
        return 6
    elif rsi >= 75 or rsi <= 25:
        return 4
    elif rsi >= 70 or rsi <= 30:
        return 2
    else:
        return 1

# Função principal de análise
def analisar_ativos():
    sinal_enviado = False
    for ativo in ATIVOS:
        handler = TA_Handler(
            symbol=ativo,
            screener="forex",
            exchange="FX_IDC",
            interval=Interval.INTERVAL_5_MINUTES
        )
        try:
            analise = handler.get_analysis()
            recomendacao = analise.summary["RECOMMENDATION"]
            rsi = analise.indicators["RSI"]

            if recomendacao in ["STRONG_BUY", "STRONG_SELL"]:
                direcao = "COMPRA" if recomendacao == "STRONG_BUY" else "VENDA"
                entrada = "R$ 2.00"
                horario_entrada = (datetime.utcnow() - timedelta(hours=3) + timedelta(minutes=3)).strftime('%H:%M')
                cliques = calcular_cliques(rsi)
                frase_clique = f"⚠ CLIQUE {cliques} VEZES {'⬆️' if direcao == 'COMPRA' else '⬇️'}"
                mensagem = (
                    f"⚡ <b>SINAL AO VIVO</b>\n"
                    f"🌐 Par: {ativo}\n"
                    f"🔄 Direção: <b>{direcao}</b>\n"
                    f"🔢 RSI: {rsi:.2f}\n"
                    f"💵 Entrada sugerida: {entrada}\n"
                    f"⏰ Entrada: <b>{horario_entrada}</b>\n"
                    f"⏳ Expiração: 5 minutos\n"
                    f"{frase_clique}\n\n"
                    f"<i>Baseado em análise ao vivo do mercado via TradingView.</i>"
                )
                enviar_mensagem(mensagem)
                sinal_enviado = True
                time.sleep(2)
        except Exception as e:
            print(f"Erro com {ativo}: {e}")

    if not sinal_enviado:
        msg = f"📉 Nenhum sinal forte encontrado às {horario_brasil()}.\n🔎 O mercado segue em análise..."
        enviar_mensagem(msg)

# Loop contínuo (a cada 3 minutos)
while True:
    print("🔁 Analisando o mercado...")
    analisar_ativos()
    print("⏱ Aguardando 3 minutos...")
    time.sleep(180)
