import requests
import time
import datetime
from tradingview_ta import TA_Handler, Interval

# Dados do Bot Telegram
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

# Lista de ativos para análise (moedas principais Pocket Option)
ATIVOS = [
    "EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCHF", "USDCAD",
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

# Função principal de análise e envio
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

            # Checar apenas sinais Moderado pra cima
            if recomendacao in ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"]:
                # Ajustar lógica de direção
                if recomendacao in ["BUY", "STRONG_BUY"]:
                    direcao = "COMPRA"
                else:
                    direcao = "VENDA"

                # Confirmar se RSI ajuda na decisão
                if (direcao == "COMPRA" and rsi < 70) or (direcao == "VENDA" and rsi > 30):
                    # Horário de entrada 3 minutos a frente
                    horario_entrada = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=3)).strftime("%H:%M")

                    # Determinar força
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
⏰ Entrada: <b>{horario_entrada}</b> (Horário de Brasília)
⏳ Expiração: <b>5 minutos</b> na Pocket Option
⚠ CLIQUE <b>{cliques} VEZES</b> na direção indicada

✅ <b>IMPORTANTE:</b> Configure o tempo de expiração para 5 minutos no gráfico.
<i>Análise real baseada em TradingView + Filtro Estratégico RSI.</i>"""

                    enviar_telegram(mensagem)
                    encontrou_sinal = True
                    break  # Só envia um sinal por análise para não confundir

        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")

    if not encontrou_sinal:
        enviar_telegram("🔎 <i>Analisando mercado...</i> Nenhum sinal favorável encontrado no momento. Aguarde...")

# Loop contínuo
while True:
    analisar_e_enviar()
    time.sleep(120)  # 2 minutos entre cada análise
