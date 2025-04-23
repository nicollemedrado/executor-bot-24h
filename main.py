import os
import requests
from flask import Flask
import threading
import time
import datetime

# Configurações
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)

def enviar_sinal_fake():
    agora = datetime.datetime.now().strftime("%H:%M")
    mensagem = f"""
📈 <b>SINAL AO VIVO DETECTADO (Simulado)</b>

<b>🪙 Ativo:</b> EURUSD  
<b>⏰ Horário:</b> {agora}  
<b>📊 Status:</b> Entrada Forte Detectada  
<b>📌 Expiração:</b> 5 minutos  
<b>🚀 DICA:</b> Dobrar a entrada se continuar subindo nos próximos 2 minutos

<i>Baseado em análise simulada para testes do canal</i>
    """

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }

    response = requests.post(url, data=payload)
    print("Sinal de teste enviado:", response.text)

def executar_teste():
    print("⏳ Enviando sinal fake de teste em 10 segundos...")
    time.sleep(10)
    enviar_sinal_fake()

# Rota web para manter ativo (Render)
@app.route('/')
def index():
    return "Bot de Teste Online"

# Executa o teste em paralelo
thread = threading.Thread(target=executar_teste, daemon=True)
thread.start()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))
