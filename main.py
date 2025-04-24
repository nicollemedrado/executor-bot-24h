import requests
import time
import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# Dados do Bot Telegram
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

# Lista de ativos (todas moedas disponíveis na Pocket Option)
ATIVOS = [
    "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURJPY", "GBPJPY", "AUDJPY", "EURGBP", "EURAUD", "CADJPY", "CHFJPY"
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

# Função principal do bot
def analisar_e_enviar():
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
            recomendacao = resultado.summary["RECOMMENDATION"]
            rsi = resultado.indicators["RSI"]

            if recomendacao in ["STRONG_BUY", "STRONG_SELL"]:
                horario_brasil = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=3)).strftime("%H:%M")
                direcao = "COMPRA" if recomendacao == "STRONG_BUY" else "VENDA"
                expiracao = "5 minutos"

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

                mensagem = f"""⚡ <b>SINAL AO VIVO</b>

🌐 Par: <b>{ativo}</b>
🔄 Direção: <b>{direcao}</b>
🔢 RSI: <b>{rsi:.2f}</b>
📶 Força: <b>{intensidade}</b>
💵 Entrada sugerida: R$ 2.00
⏰ Entrada: <b>{horario_brasil}</b>
⏳ Expiração: <b>{expiracao}</b>
⚠ CLIQUE <b>{cliques} VEZES</b> na direção indicada

<i>Análise em tempo real com base no TradingView.</i>"""

                enviar_telegram(mensagem)
                encontrou_sinal = True
                break  # envia só um por vez para não confundir

        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")

    if not encontrou_sinal:
        enviar_telegram("🔎 <i>Analisando mercado...</i> Nenhuma entrada forte encontrada. Aguarde o próximo sinal.")

# Loop contínuo
while True:
    analisar_e_enviar()
    time.sleep(120)  # 2 minutos entre cada análise
