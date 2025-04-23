import os
import requests
import time
from datetime import datetime, timedelta

# Pegando os dados do ambiente
TELEGRAM_TOKEN = os.getenv("TOKEN_TELEGRAM")
TELEGRAM_CHAT_ID = os.getenv("TOKEN_TELEGRAM_ID")

# Lista de moedas
ATIVOS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY"]

# Configuração da banca
BANCA_INICIAL = 100.0
PORCENTAGEM_ENTRADA = 0.02
INTERVALO_ANALISE = 600  # 10 minutos

def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
        print(f"[✅] Mensagem enviada: {mensagem[:60]}")
    except Exception as e:
        print(f"[❌] Erro ao enviar: {e}")

def gerar_sinal(ativo):
    horario_brasil = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M")
    direcao = "COMPRA" if int(time.time()) % 2 == 0 else "VENDA"
    valor_entrada = round(BANCA_INICIAL * PORCENTAGEM_ENTRADA, 2)

    mensagem = (
        f"⚡ <b>SINAL AO VIVO</b>\n\n"
        f"🪙 Ativo: <b>{ativo}</b>\n"
        f"⏰ Horário: <b>{horario_brasil}</b>\n"
        f"📊 Direção: <b>{direcao}</b>\n"
        f"💰 Entrada: R$ {valor_entrada}\n"
        f"⌛ Expiração: 5 minutos\n\n"
        f"<i>Baseado em simulação de sinais automatizados.</i>"
    )

    enviar_mensagem(mensagem)

def executar_bot():
    while True:
        print("🔁 Analisando mercado...")
        sinais_encontrados = False

        for ativo in ATIVOS:
            gerar_sinal(ativo)
            sinais_encontrados = True
            time.sleep(2)  # Tempo entre sinais

        if not sinais_encontrados:
            enviar_mensagem("🔎 Nenhum sinal encontrado no momento. Bot continuará analisando...")

        print("⏱️ Aguardando 10 minutos para nova análise...\n")
        time.sleep(INTERVALO_ANALISE)

# Início do bot
if __name__ == '__main__':
    executar_bot()
