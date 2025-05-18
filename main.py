import requests
import time
import datetime
import csv
from tradingview_ta import TA_Handler, Interval

# CONFIGURAÇÕES
TELEGRAM_TOKEN = "7752601078:AAHRs0Z_BUei1W7tn8Gwbjt0a1-HV7-cHTc"
TELEGRAM_CHAT_ID = "5845175811"
ARQUIVO_HISTORICO = "historico_sinais.csv"
ANTECEDENCIA_MINUTOS = 3

# LISTAS DE ATIVOS COM TIPO
MERCADOS = [
    {"tipo": "Moeda (Forex)", "screener": "forex", "exchange": "FX_IDC", "ativos": ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCHF", "EURJPY", "GBPJPY"]},
    {"tipo": "Criptomoeda", "screener": "crypto", "exchange": "BINANCE", "ativos": ["BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD"]},
    {"tipo": "Ação (Stock)", "screener": "america", "exchange": "NASDAQ", "ativos": ["AAPL", "GOOGL", "TSLA", "AMZN"]}
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

def analisar_mercado(tipo, ativos, screener, exchange):
    for ativo in ativos:
        try:
            analise_m1 = TA_Handler(symbol=ativo, screener=screener, exchange=exchange, interval=Interval.INTERVAL_1_MINUTE).get_analysis()
            analise_m5 = TA_Handler(symbol=ativo, screener=screener, exchange=exchange, interval=Interval.INTERVAL_5_MINUTES).get_analysis()
            rec_m1 = analise_m1.summary["RECOMMENDATION"]
            rec_m5 = analise_m5.summary["RECOMMENDATION"]
            rsi = analise_m1.indicators["RSI"]

            if 45 < rsi < 55:
                continue

            if rec_m1 == rec_m5 and rec_m1 in ["BUY", "SELL", "STRONG_BUY", "STRONG_SELL"]:
                direcao = "🔼 COMPRA" if "BUY" in rec_m1 else "🔽 VENDA"

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

                hora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=ANTECEDENCIA_MINUTOS)).strftime("%H:%M")

                mensagem = f"""✅ <b>SINAL DETECTADO</b>

📊 Ativo: <b>{ativo}</b>
🏷️ Tipo: <b>{tipo}</b>
📈 Direção: <b>{direcao}</b>
📉 RSI: <b>{rsi:.2f}</b>
📶 Força: <b>{intensidade}</b>
🕒 Entrada sugerida: <b>{hora}</b> (Brasília)
⌛ Expiração: <b>5 minutos</b>
🖱️ Clique <b>{cliques}x</b> na direção indicada

⚠️ Prepare o gráfico agora — entrada em {ANTECEDENCIA_MINUTOS} minutos!
📡 Fonte: {exchange.upper()}
"""
                enviar_telegram(mensagem)
                registrar_sinal([str(datetime.datetime.now()), ativo, direcao, rsi, intensidade, tipo])
                return True

        except Exception as e:
            registrar_sinal([str(datetime.datetime.now()), ativo, "ERRO", "-", "-", str(e)])
            continue

    return False

# LOOP contínuo com verificação multi-mercado
while True:
    agora = datetime.datetime.now()
    if agora.weekday() < 5 and 9 <= agora.hour < 18:
        enviado = False
        for mercado in MERCADOS:
            enviado = analisar_mercado(mercado["tipo"], mercado["ativos"], mercado["screener"], mercado["exchange"])
            if enviado:
                break
        if not enviado:
            enviar_telegram("🔍 Nenhum sinal forte detectado em moedas, criptos ou ações. Continuamos analisando o mercado...")
    time.sleep(60)
