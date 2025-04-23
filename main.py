import os
import time
import requests
from datetime import datetime
from flask import Flask
import threading

app = Flask(__name__)

# Variáveis de ambiente esperadas: TELEGRAM_TOKEN e TELEGRAM_CHAT_ID
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    # Aviso no log se variáveis não estiverem definidas
    print("ERRO: Variáveis de ambiente TELEGRAM_TOKEN e TELEGRAM_CHAT_ID não definidas!")
    # Não prosseguir sem credenciais
    raise SystemExit("Configure as variáveis de ambiente e reinicie a aplicação.")

def consultar_preco_ativo(symbol):
    """
    Consulta o preço atual do ativo usando a API pública do Yahoo Finance.
    Retorna o preço (float) em caso de sucesso ou None em caso de erro.
    """
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            # Navega na estrutura JSON para pegar o primeiro resultado
            resultado = data.get("quoteResponse", {}).get("result", [])
            if resultado:
                cotacao = resultado[0]
                preco = cotacao.get("regularMarketPrice")
                return preco
            else:
                print(f"⚠️  Nenhum resultado encontrado para o símbolo {symbol}")
                return None
        else:
            print(f"⚠️  Erro ao consultar {symbol}: Código {resp.status_code}")
            return None
    except Exception as e:
        print(f"⚠️  Exceção ao consultar {symbol}: {e}")
        return None

def enviar_sinal_telegram(ativo, hora_str, status):
    """
    Envia uma mensagem de sinal formatada para o Telegram usando a API de bots.
    """
    # Formata a mensagem no idioma português com emojis e quebras de linha
    mensagem = (
        "⚡ SINAL AO VIVO DETECTADO ⚡\n"
        f"• Ativo: {ativo}\n"
        f"• Horário: {hora_str}\n"
        f"• Status: {status}\n"
        "✅ Prepare-se para operar!"
    )
    # Endpoint da API de envio de mensagem do Telegram
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.get(api_url, params={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem})
        response.raise_for_status()  # lança erro se a resposta indicar falha
        print(f"Mensagem enviada para o Telegram (Ativo: {ativo}, Hora: {hora_str}, Status: {status})")
    except Exception as e:
        print(f"ERRO: Falha ao enviar mensagem do ativo {ativo} -> {e}")

def loop_sinais():
    """
    Loop contínuo que consulta os ativos e envia sinais a cada 10 minutos.
    """
    # Lista de ativos a serem analisados (símbolos conforme API Yahoo Finance)
    ativos = ["EURUSD=X"]  # Você pode adicionar outros símbolos aqui conforme necessidade
    # Mapeamento opcional para nomes amigáveis (remover sufixos como =X)
    nome_ativo_formatado = lambda symbol: symbol.replace("=X", "")
    
    print("🔄 Iniciando loop de análise de ativos a cada 10 minutos...")
    while True:
        hora_atual = datetime.now().strftime("%H:%M")
        for simbolo in ativos:
            ativo_nome = nome_ativo_formatado(simbolo)
            preco = consultar_preco_ativo(simbolo)
            # Aqui você implementaria a lógica de análise para decidir o status.
            # Neste exemplo, vamos definir um status fixo para demonstração:
            status = "Entrada Forte Detectada"  # Exemplo de status baseado em análise do ativo
            # Envia o sinal para o Telegram
            enviar_sinal_telegram(ativo_nome, hora_atual, status)
        # Aguarda 10 minutos antes da próxima rodada de análise
        time.sleep(600)

# Inicia o thread de background que executa o loop de sinais
thread = threading.Thread(target=loop_sinais, daemon=True)
thread.start()

# Rota básica apenas para manter o Flask ativo (pode ser utilizada para ver status)
@app.route('/')
def index():
    return "Bot de Sinais está em execução."

# Executa a aplicação Flask (usando host e porta obtidos do ambiente, conforme exigido pelo Render)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
