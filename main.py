import requests
import time
import datetime
from tradingview_ta import TA_Handler, Interval

TELEGRAM_TOKEN = "8114639244:AAFHL2WS5RAwgoxMr2VRZ00LtzAbCoKlCFY"
TELEGRAM_CHAT_ID = "-1002555783780"

ATIVOS = [
    "EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCHF", "USDCAD",
    "EURJPY", "GBPJPY", "AUDJPY", "EURGBP", "EURAUD", "CADJPY", "CHFJPY"
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

def analisar_e_enviar():
    encontrou_sinal = False

    for ativo in ATIVOS:
        try:
            analise_m1 = TA_Handler(
                symbol=ativo,
                screener="forex",
                exchange="FX_IDC",
                interval=Interval.INTERVAL_1_MINUTE
            ).get_analysis()

            analise_m5 = TA_Handler(
                symbol=ativo,
                screener="forex",
                exchange="FX_IDC",
                interval=Interval.INTERVAL_5_MINUTES
            ).get_analysis()

            recomendacao_m1 = analise_m1.summary["RECOMMENDATION"]
            recomendacao_m5 = analise_m5.summary["RECOMMENDATION"]
            rsi = analise_m1.indicators["RSI"]

            # Confirma tendência e força
            if recomendacao_m1 in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"] and recomendacao_m1 == recomendacao_m5:
                if (recomendacao_m1 in ["BUY", "STRONG_BUY"] and rsi < 70) or (recomendacao_m1 in ["SELL", "STRONG_SELL"] and rsi > 30):
                    if 45 < rsi < 55:
                        continue  # mercado lateral, pula

                    direcao = "COMPRA" if "BUY" in recomendacao_m1 else "VENDA"
                    horario_entrada = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=3)).strftime("%H:%M")

                    # Avaliação da força com base no RSI
                    if rsi >= 90 or rsi <= 10:
                        intensidade = "EXTREMAMENTE FORTE"
                        cliques = 10
                    elif rsi >= 80 or rsi <= 20:
                        intensidade = "MUITO FORTE"
                        cliques = 7
                    elif rsi >= 70 or rsi <= 30:
                        intensidade = "FORTE"
                        cliques = 5
                    elif rsi >= 60 or rsi <= 40:
                        intensidade = "MODERADA"
                        cliques = 3
                    else:
                        intensidade = "FRACA"
                        cliques = 1

                    mensagem = f"""✅ <b>ENTRADA RECOMENDADA</b>

🌐 Par: <b>{ativo}</b>
🔄 Direção: <b>{direcao}</b>
🔢 RSI: <b>{rsi:.2f}</b>
📶 Força: <b>{intensidade}</b>
⏰ Entrada sugerida: <b>{horario_entrada}</b> (Brasília)
⌛ Expiração: <b>5 minutos</b> na Pocket Option
🖱️ CLIQUE <b>{cliques}x</b> na direção indicada

<i>Análise com base em múltiplos tempos gráficos (M1 + M5) e confirmação de força RSI.</i>
"""
                    enviar_telegram(mensagem)
                    encontrou_sinal = True
                    break  # envia só um por vez

        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")

    if not encontrou_sinal:
        enviar_telegram("⚠️ <i>Análise concluída.</i> Nenhuma entrada confiável no momento. Aguardar novo sinal...")

# Loop contínuo
while True:
    analisar_e_enviar()
    time.sleep(120)  # a cada 2 minutos
