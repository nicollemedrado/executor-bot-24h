import requests
import time
import datetime

# CONFIGURAÇÕES DE ENVIO
TELEGRAM_TOKEN = "7752601078:AAHRs0Z_BUei1W7tn8Gwbjt0a1-HV7-cHTc"
TELEGRAM_CHAT_ID = "-1002555783780"

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        print("Mensagem enviada:", mensagem)
        print("Status:", response.status_code)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

# LOOP DE TESTE: envia uma mensagem a cada minuto
print("✅ Bot de Teste Iniciado - Enviando mensagens simuladas a cada minuto...")

while True:
    agora = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    mensagem = f"""🚀 <b>TESTE DE ENVIO</b>

🕒 Horário: <b>{agora}</b>
📢 Este é um <b>teste automatizado</b> para confirmar que o bot está enviando sinais no canal corretamente.

✅ Se você está vendo isso no canal, o envio está funcionando 100%.
"""
    enviar_telegram(mensagem)
    time.sleep(60)
