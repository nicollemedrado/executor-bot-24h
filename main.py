import requests
import time
import datetime
from tradingview_ta import TA_Handler, Interval

# Dados do Bot Telegram
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

# Lista de ativos para análise OTC
ATIVOS = [
    "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURJPY", "GBPJPY", "AUDJPY", "EURGBP", "EURAUD", "CADJPY", "CHFJPY",
    "NZDJPY", "GBPAUD", "AUDCAD", "AUDNZD", "EURCAD", "EURNZD"
]

# Função para enviar mensagem ao Telegram
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

# Função principal de análise
def analisar_e_enviar():
    encontrou_sinal = False

    for ativo in ATIVOS:
        try:
            analise = TA_Handler(
                symbol=ativo,
                screener="forex",
                exchange="FX_IDC",
                interval=Interval.INTERVAL_5_MINUTES  # Analisando M5 para OTC
            )
            resultado = analise.get_analysis()
            recomendacao = resultado.summary["RECOMMENDATION"]
            rsi = resultado.indicators["RSI"]
            macd = resultado.indicators["MACD.macd"]
            macd_signal = resultado.indicators["MACD.signal"]
            ema9 = resultado.indicators["EMA9"]
            ema21 = resultado.indicators["EMA21"]
            preco_atual = resultado.indicators["close"]

            # Direção
            if recomendacao in ["BUY", "STRONG_BUY"]:
                direcao = "COMPRA"
            elif recomendacao in ["SELL", "STRONG_SELL"]:
                direcao = "VENDA"
            else:
                direcao = "INDEFINIDO"

            # Definir força
            if recomendacao == "STRONG_BUY" or recomendacao == "STRONG_SELL":
                intensidade = "EXTREMAMENTE FORTE"
            elif recomendacao == "BUY" or recomendacao == "SELL":
                intensidade = "FORTE"
            else:
                intensidade = "MODERADO/FRACO"

            # Definir cliques sugeridos
            if rsi >= 90 or rsi <= 10:
                cliques = 10
            elif rsi >= 80 or rsi <= 20:
                cliques = 8
            elif rsi >= 70 or rsi <= 30:
                cliques = 6
            elif rsi >= 60 or rsi <= 40:
                cliques = 4
            else:
                cliques = 2

            # Análises extras
            confirmacoes = 0
            resumo_rsi = ""
            resumo_macd = ""
            resumo_ema = ""

            if (direcao == "COMPRA" and rsi < 30) or (direcao == "VENDA" and rsi > 70):
                confirmacoes += 1
                resumo_rsi = "RSI confirma"

            if (direcao == "COMPRA" and macd > macd_signal) or (direcao == "VENDA" and macd < macd_signal):
                confirmacoes += 1
                resumo_macd = "MACD confirma"

            if (direcao == "COMPRA" and ema9 > ema21) or (direcao == "VENDA" and ema9 < ema21):
                confirmacoes += 1
                resumo_ema = "EMA confirma"

            # Legenda de qualidade da entrada
            if confirmacoes == 3:
                conselho = "✅ Entrada EXCELENTE (3 confirmações)"
            elif confirmacoes == 2:
                conselho = "⚠️ Entrada BOA (2 confirmações)"
            elif confirmacoes == 1:
                conselho = "❌ Entrada arriscada (1 confirmação)"
            else:
                conselho = "🚫 NÃO operar (0 confirmações)"

            horario_entrada = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=3)).strftime("%H:%M")

            mensagem = f"""⚡ <b>SINAL OTC TREINO</b>

🌐 Par: <b>{ativo}</b>
🔄 Direção: <b>{direcao}</b>
📶 Força do Sinal: <b>{intensidade}</b>
🔢 RSI: <b>{rsi:.2f}</b> {resumo_rsi}
📈 MACD: <b>{macd:.2f} / {macd_signal:.2f}</b> {resumo_macd}
📊 EMA9: <b>{ema9:.4f}</b> | EMA21: <b>{ema21:.4f}</b> {resumo_ema}
💥 CLIQUE <b>{cliques} VEZES</b> na direção indicada
⏰ Entrada: <b>{horario_entrada}</b> (Horário de Brasília)
⏳ Expiração: <b>10 minutos</b>

📋 {conselho}

<i>Análise OTC baseada em TradingView + Filtros Inteligentes.</i>"""

            enviar_telegram(mensagem)
            encontrou_sinal = True
            break

        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")

    if not encontrou_sinal:
        enviar_telegram("🔎 Nenhum sinal com confirmação suficiente. Aguardando próxima oportunidade...")

# Loop de análise a cada 2 minutos
while True:
    analisar_e_enviar()
    time.sleep(120)
