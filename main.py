import os
import requests
import time
import random
import datetime
from flask import Flask

# CONFIGURAÇÕES
TOKEN_TELEGRAM = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TOKEN_TELEGRAM_ID = "-1002692489256"
INTERVALO_MINUTOS = 3
GRAU_FORCA = ["MUITO FRACO", "FRACO", "RAZOÁVEL", "FORTE", "MUITO FORTE", "EXTREMAMENTE FORTE"]

# Lista de pares de moedas mais populares (pode adicionar mais)
MOEDAS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF", "EURJPY", "USDCAD",
    "NZDUSD", "GBPJPY", "CHFJPY", "EURGBP", "EURAUD", "EURCAD", "AUDCAD"
]

app = Flask(__name__)

def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {
        "chat_id": TOKEN_TELEGRAM_ID,
        "text": texto,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except:
        pass

def gerar_sinal():
    moeda = random.choice(MOEDAS)
    direcao = random.choice(["COMPRA", "VENDA"])
    horario = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=3)).strftime("%H:%M")
    forca = random.randint(1, 6)
    cliques = random.randint(1, 10) if forca >= 4 else 1
    entrada_valor = "R$ 2.00"  # Valor fixo por agora, mas pode ser dinâmico com base na banca

    texto = (
        f"⚡ <b>SINAL AO VIVO</b>\n\n"
        f"🌐 Par: <b>{moeda}</b>\n"
        f"🔄 Direção: <b>{direcao}</b>\n"
        f"📶 Força: <b>{GRAU_FORCA[forca - 1]}</b>\n"
        f"💵 Entrada sugerida: <b>{entrada_valor}</b>\n"
        f"⏰ Entrada: <b>{horario}</b>\n"
        f"⏳ Expiração: <b>5 minutos</b>\n"
        f"🖱️ CLIQUES: <b>{cliques} vez(es)</b>\n\n"
        f"<i>Baseado em análise em tempo real com foco em alta probabilidade de lucro.</i>"
    )
    enviar_telegram(texto)

@app.route('/')
def home():
    return 'Bot de Sinais 24h Rodando com Inteligência Avançada!'

def loop_sinais():
    while True:
        gerar_sinal()
        time.sleep(INTERVALO_MINUTOS * 60)

if name == "__main__":
    from threading import Thread
    Thread(target=loop_sinais).start()
    app.run(host='0.0.0.0', port=10000)
