import requests
import time
import datetime

TOKEN_TELEGRAM = "7810390855:AAGAUM-z_m4xMSvpF446ITLwujX_aHhTW68"
TOKEN_TELEGRAM_ID = "-1002692489256"

# Configurações
ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "EURJPY",
    "BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD"
]
VALOR_BANCA = 100
PORCENTAGEM_ENTRADA = 0.02  # 2%
INTERVALO_ANALISE = 120  # 2 minutos

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    data = {
        "chat_id": TOKEN_TELEGRAM_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def analisar_rsi():
    algum_sinal_enviado = False

    for ativo in ATIVOS:
        try:
            url = f"https://api.taapi.io/rsi?secret=demo&exchange=binance&symbol={ativo}/USDT&interval=1m"
            resposta = requests.get(url)
            rsi = resposta.json().get("value", 50)

            agora = (datetime.datetime.utcnow() - datetime.timedelta(hours=3) + datetime.timedelta(minutes=2)).strftime("%H:%M")
            valor_entrada = round(VALOR_BANCA * PORCENTAGEM_ENTRADA, 2)

            if rsi <= 30:
                mensagem = (
                    f"⚡ <b>SINAL AO VIVO</b>\n\n"
                    f"🌐 Par: {ativo}\n"
                    f"🔄 Direção: <b>COMPRA</b>\n"
                    f"🔢 RSI: {round(rsi, 2)}\n"
                    f"💵 Entrada sugerida: R$ {valor_entrada}\n"
                    f"⏰ Entrada: {agora}\n"
                    f"⏳ Expiração: 2 minutos\n"
                    f"⚠ CLIQUE APENAS UMA VEZ (sinal forte)\n\n"
                    f"<i>Baseado em RSI abaixo de 30 (reversão de baixa).</i>"
                )
                enviar_telegram(mensagem)
                algum_sinal_enviado = True
                break

            elif rsi >= 70:
                mensagem = (
                    f"⚡ <b>SINAL AO VIVO</b>\n\n"
                    f"🌐 Par: {ativo}\n"
                    f"🔄 Direção: <b>VENDA</b>\n"
                    f"🔢 RSI: {round(rsi, 2)}\n"
                    f"💵 Entrada sugerida: R$ {valor_entrada}\n"
                    f"⏰ Entrada: {agora}\n"
                    f"⏳ Expiração: 2 minutos\n"
                    f"⚠ CLIQUE APENAS UMA VEZ (sinal forte)\n\n"
                    f"<i>Baseado em RSI acima de 70 (reversão de alta).</i>"
                )
                enviar_telegram(mensagem)
                algum_sinal_enviado = True
                break

        except Exception as e:
            print(f"Erro ao analisar {ativo}: {e}")

    if not algum_sinal_enviado:
        enviar_telegram("🔎 <b>Analisando mercado...</b>\n\nNenhuma entrada forte detectada ainda. O bot continua monitorando em tempo real.")

def loop():
    while True:
        print("🔁 Analisando mercado...")
        analisar_rsi()
        time.sleep(INTERVALO_ANALISE)

if __name__ == "__main__":
    loop()
