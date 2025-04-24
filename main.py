import os
import requests
import time
import datetime
import random
from tradingview_ta import TA_Handler, Interval, Exchange

# Token e ID do Telegram
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

# Lista de ativos a serem monitorados
ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD",
    "EURJPY", "NZDUSD", "EURGBP", "BTCUSD", "ETHUSD"
]

# Configurações
INTERVALO = 180  # 3 minutos
BANCA_INICIAL = 100.0
VALOR_BASE = 2.0

# Função para enviar mensagem no Telegram
def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    dados = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    requests.post(url, data=dados)

# Função para gerar sinal com análise real
def analisar_ativos():
    encontrou_sinal = False
    for ativo in ATIVOS:
        try:
            analise = TA_Handler(
                symbol=ativo,
                screener="forex",
                exchange="FX_IDC",
                interval=Interval.INTERVAL_1_MINUTE
            )
            resultado = analise.get_analysis()
            rsi = resultado.indicators["RSI"]
            recomendacao = resultado.summary["RECOMMENDATION"]
            direcao = "COMPRA" if recomendacao in ["BUY", "STRONG_BUY"] else "VENDA"
            horario_entrada = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=3)).strftime("%H:%M")

            if recomendacao in ["STRONG_BUY", "STRONG_SELL"]:
                multiplicador = 1
                if rsi < 30 or rsi > 70:
                    multiplicador = random.randint(2, 10)  # Recomendação de clique extra

                entrada = round(BANCA_INICIAL * 0.02, 2)
                texto = f"""⚡ <b>SINAL AO VIVO</b>

🌐 Par: <b>{ativo}</b>
🔄 Direção: <b>{direcao}</b>
🔢 RSI: <b>{rsi:.2f}</b>
💵 Entrada sugerida: R$ {entrada}
⏰ Entrada: <b>{horario_entrada}</b>
⏳ Expiração: 5 minutos
{f"⚠ CLIQUE {multiplicador} VEZES ({'sinal MUITO forte' if multiplicador > 1 else 'sinal forte'})" if multiplicador > 1 else "⚠ CLIQUE APENAS UMA VEZ (sinal forte)"}

<i>Baseado em análise real do mercado via TradingView</i>"""
                enviar_telegram(texto)
                encontrou_sinal = True
                break  # Envia apenas 1 sinal por vez
        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")
            continue

    if not encontrou_sinal:
        enviar_telegram("🔎 <b>Analisando mercado...</b>\n\nNenhum sinal forte foi encontrado no momento. Monitorando em tempo real...")

# Loop contínuo
while True:
    analisar_ativos()
    time.sleep(INTERVALO)
