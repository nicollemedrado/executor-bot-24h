import requests
import time
import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# Dados do Bot Telegram
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

# Lista de ativos (moedas da Pocket Option)
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

# Função principal
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
            justificativa = ""
            
            # Correção inteligente de direção
            if recomendacao == "STRONG_BUY":
                if rsi > 70:
                    direcao = "VENDA"
                    justificativa = "(RSI sobrecomprado — inversão estratégica)"
                else:
                    direcao = "COMPRA"
            elif recomendacao == "STRONG_SELL":
                if rsi < 30:
                    direcao = "COMPRA"
                    justificativa = "(RSI sobrevendido — inversão estratégica)"
                else:
                    direcao = "VENDA"
            else:
                continue  # ignora sinais fracos

            # Força e cliques baseados no RSI
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

            # Horário da entrada com +3 min
            horario_entrada = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=3)).strftime("%H:%M")

            mensagem = f"""⚡ <b>SINAL AO VIVO</b>

🌐 Par: <b>{ativo}</b>
🔄 Direção: <b>{direcao}</b> {justificativa}
🔢 RSI: <b>{rsi:.2f}</b>
📶 Força: <b>{intensidade}</b>
💵 Entrada sugerida: R$ 2.00
⏰ Entrada: <b>{horario_entrada}</b> (Horário de Brasília)
⏳ Expiração: <b>5 minutos</b> na Pocket Option
⚠ CLIQUE <b>{cliques} VEZES</b> na direção indicada

✅ <b>IMPORTANTE:</b> Configure a operação para durar <b>5 minutos</b> no gráfico da plataforma.

<i>Análise em tempo real com base no TradingView + filtro estratégico RSI.</i>"""

            enviar_telegram(mensagem)
            encontrou_sinal = True
            break

        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")

    if not encontrou_sinal:
        enviar_telegram("🔎 <i>Analisando mercado...</i> Nenhum sinal forte detectado no momento. Aguarde...")

# Loop contínuo
while True:
    analisar_e_enviar()
    time.sleep(120)
