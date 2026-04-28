import requests
import os
import sys

# ══════════════════════════════════════════════
# TESTE DE CONECTIVIDADE - DIAGNÓSTICO
# ══════════════════════════════════════════════

# 1. Tenta ler as chaves do "Servidor" (GitHub Secrets)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def testar_conexao():
    print(" 🛠 INICIANDO DIAGNÓSTICO DE REDE...")
    print(f" 📦 Token carregado: {'✅ SIM' if TOKEN else '❌ NÃO'}")
    print(f" 📦 Chat ID carregado: {'✅ SIM' if CHAT_ID else '❌ NÃO'}")

    if not TOKEN or not CHAT_ID:
        print("\n 🚨 ERRO: As chaves não foram encontradas no ambiente do GitHub.")
        print(" Verifique se os nomes nos 'Secrets' estão EXATAMENTE como 'TELEGRAM_TOKEN' e 'TELEGRAM_CHAT_ID'.")
        sys.exit(1)

    # 2. Tenta o "Ping" (Envio de Mensagem)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "🚀 *TESTE DE CONEXÃO:* O bot está conseguindo falar com o Telegram via GitHub Actions!",
        "parse_mode": "Markdown"
    }

    try:
        print("\n 📡 Enviando pacote para o Telegram...")
        r = requests.post(url, json=payload, timeout=10)
        
        if r.status_code == 200:
            print(" ✅ SUCESSO: Mensagem enviada! Verifique o seu grupo no Telegram.")
        else:
            print(f" ❌ ERRO NA API: O Telegram retornou o erro {r.status_code}")
            print(f" Resposta: {r.text}")
            
    except Exception as e:
        print(f" ❌ ERRO DE CONEXÃO: {str(e)}")

if __name__ == "__main__":
    testar_conexao()
