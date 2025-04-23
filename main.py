import os
import requests

# Dados do ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Função para enviar mensagem
def enviar_mensagem(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    print("Resposta:", response.text)

# Envia mensagem de teste
enviar_mensagem("⚡️ <b>Teste do bot Executor</b> enviado com sucesso para o canal @SalaFantasmaBR ⚡️")
