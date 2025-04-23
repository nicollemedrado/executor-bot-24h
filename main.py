import os
import requests
import time
import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# =========================
# CONFIGURAÇÕES DO BOT
# =========================
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

# Lista completa de pares de moedas da Pocket Option (exemplos — adicione mais conforme necessário)
ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY", "NZDUSD",
    "EURGBP", "EURCAD", "GBPCAD", "GBPJPY", "AUDJPY", "AUDCAD", "CHFJPY", "NZDJPY",
    "CADJPY", "AUDNZD", "EURNZD", "GBPAUD", "GBPNZD", "USDNOK", "USDSEK", "USDHKD"
]

VALOR_BANCA = 100.0
PORCENTAGEM_ENTRADA = 0.02  # 2% da banca
INTERVALO_ANALISE = 600  # 10 minutos

# =========================
# FUNÇÕES
# =========================
def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
        print("✅ Mensagem enviada")
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def analisar_ativo(simbolo):
    try:
        handler = TA_Handler(
            symbol=simbolo,
            exchange="FX_IDC",
            screener="forex",
            interval=Interval.INTERVAL_5_MINUTES
        )
        analise = handler.get_analysis()
        rsi = analise.indicators.get("RSI", 50)
        recomendacao = analise.summary["RECOMMENDATION"]
        estrelas = "⭐" * analise.summary.get("BUY", 0) if recomendacao == "BUY" else "⭐" * analise.summary.get("SELL", 0)

        agora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%H:%M")
        entrada = round(VALOR_BANCA * PORCENTAGEM_ENTRADA, 2)

        if recomendacao in ["STRONG_BUY", "STRONG_SELL"]:
            direcao = "COMPRA" if recomendacao == "STRONG_BUY" else "VENDA"
            clique_msg = "🟢 Clique 1 vez." if rsi < 60 and rsi > 40 else "⚠️ Clique 2 ou mais vezes se a força continuar."
            tendencia = "Alta" if rsi > 70 else "Baixa" if rsi < 30 else "Neutra"

            mensagem = (
                f"<b>SINAL AO VIVO</b>

"
                f"🧭 Par: <b>{simbolo}</b>
"
                f"📈 Direção: <b>{direcao}</b>
"
                f"💸 Entrada sugerida: <b>R$ {entrada}</b>
"
                f"⏰ Entrar às: <b>{agora}</b>
"
                f"⌛ Expiração: <b>5 minutos</b>
"
                f"🔍 RSI: <b>{rsi:.2f} ({tendencia})</b>
"
                f"{clique_msg}
"
                f"{estrelas}

"
                f"<i>Baseado em análise ao vivo via TradingView.</i>"
            )
            enviar_mensagem(mensagem)
            return True
    except Exception as e:
        print(f"Erro em {simbolo}: {e}")
    return False

# =========================
# LOOP DO BOT
# =========================
while True:
    print("🔁 Verificando sinais...")
    sinal_encontrado = False
    for par in ATIVOS:
        resultado = analisar_ativo(par)
        if resultado:
            sinal_encontrado = True
            time.sleep(2)

    if not sinal_encontrado:
        agora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%H:%M")
        enviar_mensagem(f"⚪ Nenhum sinal forte identificado às <b>{agora}</b>. Monitorando o mercado ao vivo...")

    print("⏳ Aguardando próximo ciclo de análise...")
    time.sleep(INTERVALO_ANALISE)
