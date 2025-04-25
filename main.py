import requests
import time
import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

# === CONFIGURAÇÕES DO TELEGRAM ===
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"

# === LISTA DE ATIVOS A ANALISAR ===
ATIVOS = [
    "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURJPY", "GBPJPY", "AUDJPY", "EURGBP", "EURAUD", "CADJPY", "CHFJPY"
]

# === FUNÇÃO PARA ENVIAR SINAL NO TELEGRAM ===
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

# === FUNÇÃO PRINCIPAL ===
def analisar_e_enviar():
    melhor_sinal = None
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
            macd = resultado.indicators.get("MACD.macd", 0)
            macd_signal = resultado.indicators.get("MACD.signal", 0)
            ema9 = resultado.indicators.get("EMA9", 0)
            ema21 = resultado.indicators.get("EMA21", 0)
            preco = resultado.indicators.get("close", 0)

            direcao = None
            justificativa = []
            indicadores = []

            # Lógica inteligente de confluência
            if rsi < 30:
                indicadores.append("RSI sobrevendido")
                direcao = "COMPRA"
            elif rsi > 70:
                indicadores.append("RSI sobrecomprado")
                direcao = "VENDA"

            if macd > macd_signal:
                indicadores.append("MACD cruzando para cima")
                if not direcao:
                    direcao = "COMPRA"
            elif macd < macd_signal:
                indicadores.append("MACD cruzando para baixo")
                if not direcao:
                    direcao = "VENDA"

            if preco > ema9 > ema21:
                indicadores.append("EMA9 acima da EMA21")
                if not direcao:
                    direcao = "COMPRA"
            elif preco < ema9 < ema21:
                indicadores.append("EMA9 abaixo da EMA21")
                if not direcao:
                    direcao = "VENDA"

            # Se não tiver no mínimo 2 confirmações, ignora
            if len(indicadores) < 2 or not direcao:
                continue

            # Pega o horário com 3 minutos de antecedência
            horario_entrada = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=3)).strftime("%H:%M")

            mensagem = f"""⚡ <b>SINAL AO VIVO</b>

📊 Par: <b>{ativo}</b>
🔄 Direção: <b>{direcao}</b>
📶 Força técnica: <b>{' + '.join(indicadores)}</b>

📈 RSI: <b>{rsi:.2f}</b>
📉 MACD: <b>{macd:.2f}</b> | Sinal: <b>{macd_signal:.2f}</b>
📊 EMA9: <b>{ema9:.4f}</b> | EMA21: <b>{ema21:.4f}</b>
💰 Preço atual: <b>{preco:.4f}</b>

🧠 <b>INTERPRETAÇÃO:</b> {' + '.join(indicadores)}

📌 Indicadores para ativar no gráfico: <b>RSI • MACD • EMA 9/21</b>
⏰ Entrada sugerida: <b>{horario_entrada}</b> (Horário de Brasília)
⏳ Expiração: <b>5 minutos</b> na Pocket Option

<i>Análise técnica em tempo real com confirmação de múltiplos indicadores.</i>
"""

            melhor_sinal = mensagem
            break  # envia só um por vez

        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")

    if melhor_sinal:
        enviar_telegram(melhor_sinal)
    else:
        enviar_telegram("🔎 Nenhum sinal forte detectado agora. Monitorando...")

# === LOOP CONTÍNUO ===
while True:
    analisar_e_enviar()
    time.sleep(180)  # 3 minutos entre análises
