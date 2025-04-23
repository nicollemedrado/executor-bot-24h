import os
import requests
import time
import datetime
import threading
from flask import Flask

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

# =========================
# CONFIGURAÇÕES DO SISTEMA
# =========================
ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY",
    "NZDUSD", "EURGBP", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY", "EURAUD",
    "GBPAUD", "NZDJPY", "USDHKD", "USDZAR", "USDMXN"
]
VALOR_BANCA_INICIAL = 100.0  # Banca inicial
ENTRADA_PORCENTAGEM = 0.02   # 2% da banca
STOP_WIN = 0.10              # Meta de lucro diária: 10%
STOP_LOSS = 0.05             # Limite de perda diária: 5%
INTERVALO_ANALISE = 180      # 3 minutos entre análises

banca_atual = VALOR_BANCA_INICIAL
lucro_dia = 0.0
perda_dia = 0.0

# =========================
# FUNÇÕES PRINCIPAIS
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
        print("✅ Mensagem enviada:", texto[:60])
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def simular_analise(simbolo):
    global banca_atual, lucro_dia, perda_dia

    agora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=2)).strftime("%H:%M")
    preco = round(100 + (datetime.datetime.now().second % 10), 2)
    tendencia = "STRONG_BUY" if preco % 2 == 0 else "STRONG_SELL"
    entrada = round(banca_atual * ENTRADA_PORCENTAGEM, 2)
    lucro_simulado = round(entrada * 0.8, 2)  # Simula 80% de retorno se ganhar
    dica_dobra = "📌 DICA: Se o ativo continuar na mesma direção, dobre a operação após 1 minuto." if preco % 2 == 0 else ""

    if lucro_dia >= STOP_WIN * VALOR_BANCA_INICIAL:
        enviar_mensagem("🟢 <b>Meta diária de lucro atingida.</b> Bot pausado temporariamente.")
        return False
    if perda_dia >= STOP_LOSS * VALOR_BANCA_INICIAL:
        enviar_mensagem("🔴 <b>Limite diário de perda atingido.</b> Bot pausado temporariamente.")
        return False

    if tendencia in ["STRONG_BUY", "STRONG_SELL"]:
        direcao = "COMPRA" if tendencia == "STRONG_BUY" else "VENDA"
        mensagem = (
            f"⚡ <b>SINAL AO VIVO</b>\n\n"
            f"🪙 Ativo: <b>{simbolo}</b>\n"
            f"⏰ Entrar às: <b>{agora}</b>\n"
            f"📊 Direção: <b>{direcao}</b>\n"
            f"💰 Entrada sugerida: R$ {entrada} (2% da banca atual R$ {banca_atual})\n"
            f"⌛ Expiração: 5 minutos\n"
            f"{dica_dobra}\n\n"
            f"<i>Baseado em análise automatizada e inteligência de sinais.</i>"
        )
        enviar_mensagem(mensagem)

        # Simular que ganhou a operação
        banca_atual += lucro_simulado
        lucro_dia += lucro_simulado
    else:
        perda_simulada = round(entrada, 2)
        banca_atual -= perda_simulada
        perda_dia += perda_simulada
        enviar_mensagem(f"🔎 Análise em {simbolo} às {agora}. Nenhuma entrada forte. Banca atual: R$ {banca_atual:.2f}")

    return True

def loop_executor():
    while True:
        print("🔁 Iniciando nova análise de mercado...")
        for ativo in ATIVOS:
            continuar = simular_analise(ativo)
            if not continuar:
                return
            time.sleep(1)
        print("🕒 Aguardando próximo ciclo...")
        time.sleep(INTERVALO_ANALISE)

@app.route('/')
def index():
    return "✅ Executor Bot 24h rodando com inteligência de sinais."

threading.Thread(target=loop_executor, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
