import os
import requests
import time
import datetime
import threading
from flask import Flask

# ============================
# CONFIGURAÇÕES INICIAIS
# ============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

Banca = 1000.0
ValorEntrada = 5.0
MetaLucro = 200.0
LimitePerda = 100.0
LucroAcumulado = 0.0
PerdaAcumulada = 0.0
IntervaloAnalise = 600  # 10 minutos

ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY"
]

app = Flask(__name__)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
        print("Mensagem enviada com sucesso.")
    except:
        print("Erro ao enviar mensagem para o Telegram.")

def analisar_forca():
    return int(datetime.datetime.now().second % 10 + 1)  # Simulação de força (1-10)

def formatar_sinal(ativo, direcao, cliques):
    agora = datetime.datetime.now().strftime("%H:%M:%S")
    return (
        f"\u26a1 <b>SINAL TURBO</b>\n"
        f"<b>{ativo}</b>\n"
        f"<b>DIRE\u00c7\u00c3O:</b> {direcao}\n"
        f"<b>CLIQUES:</b> {cliques}x\n"
        f"<b>EXPIRA\u00c7\u00c3O:</b> 10 SEGUNDOS\n"
        f"<b>HOR\u00c1RIO:</b> {agora}"
    )

def simular_resultado(cliques):
    global LucroAcumulado, PerdaAcumulada
    acertos = int(cliques * 0.7)  # Simulação: 70% win
    erros = cliques - acertos
    lucro = acertos * ValorEntrada * 0.92
    perda = erros * ValorEntrada
    LucroAcumulado += lucro
    PerdaAcumulada += perda

def verificar_limites():
    if LucroAcumulado >= MetaLucro:
        enviar_telegram("\ud83d\udd35 <b>Meta de lucro do dia atingida. Parando o bot.</b>")
        return False
    if PerdaAcumulada >= LimitePerda:
        enviar_telegram("\ud83d\udd34 <b>Limite de perda do dia atingido. Parando o bot.</b>")
        return False
    return True

def ciclo():
    while True:
        if not verificar_limites():
            break

        enviado = False
        for ativo in ATIVOS:
            if not verificar_limites():
                break
            forca = analisar_forca()
            if forca >= 5:
                direcao = "COMPRA" if forca % 2 == 0 else "VENDA"
                mensagem = formatar_sinal(ativo, direcao, forca)
                enviar_telegram(mensagem)
                simular_resultado(forca)
                enviado = True
                break  # envia apenas 1 sinal por ciclo

        if not enviado:
            agora = datetime.datetime.now().strftime("%H:%M:%S")
            enviar_telegram(f"\u26aa <i>({agora}) Nenhum sinal forte encontrado. Analisando o mercado...</i>")

        print("Aguardando o pr\u00f3ximo ciclo...")
        time.sleep(IntervaloAnalise)

@app.route("/")
def home():
    return "Bot Executor de Setas Turbo ativo!"

threading.Thread(target=ciclo).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
