import requests
import time
import datetime
from tradingview_ta import TA_Handler, Interval

# === CONFIGURAÇÕES DO TELEGRAM ===
TELEGRAM_TOKEN = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TELEGRAM_CHAT_ID = "-1002692489256"  # SalaFantasmaBR

# === LISTA DE ATIVOS DISPONÍVEIS NA POCKET OTC ===
ATIVOS = [
    "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURJPY", "GBPJPY", "AUDJPY", "EURGBP", "EURAUD", "CADJPY", "CHFJPY",
    "EURNZD", "GBPAUD", "GBPCAD", "NZDJPY", "AUDCAD", "AUDNZD"
]

# === FUNÇÃO PARA ENVIAR MENSAGEM AO TELEGRAM ===
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

# === FUNÇÃO PRINCIPAL DE ANÁLISE ===
def analisar_e_enviar():
    encontrou_sinal = False

    for ativo in ATIVOS:
        try:
            analise = TA_Handler(
                symbol=ativo,
                screener="forex",
                exchange="FX_IDC",
                interval=Interval.INTERVAL_5_MINUTES  # OTC trabalha mais lento, vamos analisar M5
            )
            resultado = analise.get_analysis()

            # Indicadores
            rsi = resultado.indicators["RSI"]
            macd = resultado.indicators.get("MACD.macd", 0)
            macd_signal = resultado.indicators.get("MACD.signal", 0)
            ema9 = resultado.indicators.get("EMA9", 0)
            ema21 = resultado.indicators.get("EMA21", 0)
            preco = resultado.indicators.get("close", 0)
            recomendacao = resultado.summary["RECOMMENDATION"]

            confirmacoes = []
            direcao = None

            # RSI
            if rsi < 30:
                confirmacoes.append("RSI sobrevendido")
                direcao = "COMPRA"
            elif rsi > 70:
                confirmacoes.append("RSI sobrecomprado")
                direcao = "VENDA"

            # MACD
            if macd > macd_signal:
                confirmacoes.append("MACD cruzando para cima")
                if not direcao:
                    direcao = "COMPRA"
            elif macd < macd_signal:
                confirmacoes.append("MACD cruzando para baixo")
                if not direcao:
                    direcao = "VENDA"

            # EMA
            if ema9 > ema21:
                confirmacoes.append("EMA9 acima EMA21")
                if not direcao:
                    direcao = "COMPRA"
            elif ema9 < ema21:
                confirmacoes.append("EMA9 abaixo EMA21")
                if not direcao:
                    direcao = "VENDA"

            # Se não houver 3 confirmações, ignora
            if len(confirmacoes) < 3 or not direcao:
                continue

            # Definir força
            if rsi <= 10 or rsi >= 90:
                forca = "EXTREMAMENTE FORTE"
                cliques = 12
            elif rsi <= 20 or rsi >= 80:
                forca = "MUITO FORTE"
                cliques = 9
            elif rsi <= 30 or rsi >= 70:
                forca = "FORTE"
                cliques = 6
            else:
                forca = "MODERADA"
                cliques = 3

            if forca not in ["FORTE", "MUITO FORTE", "EXTREMAMENTE FORTE"]:
                continue

            # Ajustar horário com 3 minutos de antecedência
            horario_entrada = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=3)).strftime("%H:%M")

            mensagem = f"""⚡ <b>SINAL OTC TREINO</b>

🌐 Par: <b>{ativo}</b>
🔄 Direção: <b>{direcao}</b>
📶 Força: <b>{forca}</b>
🔢 RSI: <b>{rsi:.2f}</b>
📈 MACD: <b>{macd:.2f}</b> | Sinal: <b>{macd_signal:.2f}</b>
📊 EMA9: <b>{ema9:.4f}</b> | EMA21: <b>{ema21:.4f}</b>
💰 Preço atual: <b>{preco:.4f}</b>

💥 <b>CLIQUE {cliques} VEZES</b> na direção indicada
⏰ Entrada: <b>{horario_entrada}</b> (Horário de Brasília)
⏳ Expiração sugerida: <b>10 minutos</b>

<i>Análise OTC baseada em RSI + MACD + EMA (modo treino).</i>"""

            enviar_telegram(mensagem)
            encontrou_sinal = True
            break

        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")

    if not encontrou_sinal:
        enviar_telegram("🔎 Nenhum sinal confiável encontrado. Aguardando nova oportunidade...")

# === LOOP DE ANÁLISE A CADA 2 MINUTOS ===
while True:
    analisar_e_enviar()
    time.sleep(120)
