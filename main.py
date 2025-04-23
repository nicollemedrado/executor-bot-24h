import os
import requests
import time
from datetime import datetime, timedelta
from tradingview_ta import TA_Handler, Interval, Exchange

# ====== Configuração fixa com seus dados ======
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

# ====== Lista completa de ativos populares da Pocket Option ======
ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY",
    "EURGBP", "NZDUSD", "EURCHF", "CADJPY", "CHFJPY", "AUDJPY", "GBPJPY",
    "EURNZD", "AUDCAD", "NZDJPY", "GBPCAD", "GBPAUD", "USDMXN", "USDZAR",
    "BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "BCHUSD",
    "TSLA", "AAPL", "AMZN", "MSFT", "META"
]

BANCA_INICIAL = 100.0
PORCENTAGEM_ENTRADA = 0.02
STOP_WIN = 0.10  # 10%
STOP_LOSS = 0.05  # 5%
INTERVALO_ANALISE = 600  # 10 minutos

banca_atual = BANCA_INICIAL
lucro_dia = 0.0
perda_dia = 0.0

# ====== Função de envio de mensagem Telegram ======
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

# ====== Função principal de análise ======
def analisar_ativo(simbolo):
    global banca_atual, lucro_dia, perda_dia

    handler = TA_Handler(
        symbol=simbolo,
        screener="forex",
        exchange="FX_IDC",
        interval=Interval.INTERVAL_5_MINUTES
    )

    try:
        analise = handler.get_analysis()
        tendencia = analise.summary["RECOMMENDATION"]
        forca = analise.summary.get("BUY") if tendencia == "STRONG_BUY" else analise.summary.get("SELL")
        estrelas = min(int(forca), 5)
        agora = datetime.utcnow() - timedelta(hours=3)
        entrada_em = (agora + timedelta(minutes=2)).strftime("%H:%M")  # 2 minutos de antecedência
        entrada = round(banca_atual * PORCENTAGEM_ENTRADA, 2)

        if lucro_dia >= STOP_WIN * BANCA_INICIAL:
            enviar_mensagem("🟢 <b>Meta de lucro atingida!</b> Operações pausadas por hoje.")
            return

        if perda_dia >= STOP_LOSS * BANCA_INICIAL:
            enviar_mensagem("🔴 <b>Limite de perda alcançado!</b> Operações pausadas por hoje.")
            return

        if tendencia in ["STRONG_BUY", "STRONG_SELL"]:
            direcao = "COMPRA" if tendencia == "STRONG_BUY" else "VENDA"
            dica_dobra = "📌 DICA: Se continuar forte, dobre a próxima entrada." if estrelas >= 4 else ""
            mensagem = (
                f"⚡ <b>SINAL AO VIVO</b>\n\n"
                f"💱 Ativo: <b>{simbolo}</b>\n"
                f"⏰ Entrada às: <b>{entrada_em}</b>\n"
                f"📊 Direção: <b>{direcao}</b>\n"
                f"💸 Valor: R$ {entrada}\n"
                f"⌛ Expiração: 5 minutos\n"
                f"⭐ Força: {'⭐' * estrelas}\n"
                f"{dica_dobra}\n\n"
                f"<i>Baseado em análise real do mercado via TradingView.</i>"
            )
            enviar_mensagem(mensagem)
            print("Sinal enviado para", simbolo)
            return

        print("[INFO] Nenhum sinal forte para:", simbolo)

    except Exception as e:
        print("Erro em", simbolo, ":", e)

# ====== Loop principal de execução ======
def executar_bot():
    while True:
        print("Iniciando análise...")
        houve_sinal = False

        for ativo in ATIVOS:
            analisar_ativo(ativo)
            time.sleep(2)

        if not houve_sinal:
            enviar_mensagem("🔎 Analisando mercado... Nenhum sinal forte detectado.")

        time.sleep(INTERVALO_ANALISE)

# ====== Início ======
if __name__ == '__main__':
    executar_bot()
