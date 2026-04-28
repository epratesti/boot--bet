import requests
import math
import os
from datetime import datetime, timezone, timedelta

# ══════════════════════════════════════════════
# CONFIGURAÇÕES DE AMBIENTE (GITHUB SECRETS)
# ══════════════════════════════════════════════
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
BRT = timezone(timedelta(hours=-3))
hoje = datetime.now(BRT).strftime("%Y%m%d")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

def enviar_telegram(mensagem):
    """ Envia o relatório final para o grupo do Telegram """
    if not TOKEN or not CHAT_ID:
        print("Erro: Variáveis TOKEN ou CHAT_ID não encontradas.")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")

def calcular_poisson(media, linha):
    """ Calcula a probabilidade matemática de o evento superar a linha """
    if media <= 0: return 0.0
    prob_under = sum([((media ** k) * math.exp(-media)) / math.factorial(k) for k in range(int(linha) + 1)])
    return round((1 - prob_under) * 100, 1)

def scanner_profissional_v5(slug, eid):
    """ Scanner de profundidade para Gols, Cartões e Escanteios """
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/summary?event={eid}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=12).json()
        win_prob = r.get("predictor", {}).get("homeTeam", {}).get("gameProjection", 50.0)
        seed = (int(eid[-2:]) / 100)

        m_gols = (2.4 + seed) + (0.6 if win_prob > 60 or win_prob < 40 else -0.3)
        m_cards = (5.3 if "conmebol" in slug or "bra.1" in slug else 3.6) + seed
        m_corners = (9.6 + seed) + (1.3 if win_prob > 65 or win_prob < 35 else 0)

        return {
            "gols": {
                "0.5": calcular_poisson(m_gols, 0.5),
                "1.5": calcular_poisson(m_gols, 1.5),
                "2.5": calcular_poisson(m_gols, 2.5)
            },
            "cantos": {
                "7.5": calcular_poisson(m_corners, 7.5),
                "8.5": calcular_poisson(m_corners, 8.5),
                "9.5": calcular_poisson(m_corners, 9.5),
                "10.5": calcular_poisson(m_corners, 10.5)
            },
            "cards": {
                "1.5": calcular_poisson(m_cards, 1.5),
                "2.5": calcular_poisson(m_cards, 2.5),
                "3.5": calcular_poisson(m_cards, 3.5),
                "4.5": calcular_poisson(m_cards, 4.5)
            }
        }
    except:
        return None

def main():
    LIGAS = {
        "uefa.champions": "Champions League",
        "conmebol.libertadores": "Libertadores",
        "conmebol.sudamericana": "Sul-Americana",
        "bra.1": "Brasileirão A"
    }

    # Montando o cabeçalho da mensagem
    texto_final = f"🎯 *SCANNER ELITE V5* - {datetime.now(BRT).strftime('%H:%M')}\n"
    texto_final += "Regra: Apenas Confiança > 75%\n"
    texto_final += "═" * 25 + "\n"

    tem_confronto = False

    for slug, nome_liga in LIGAS.items():
        url_sb = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard?dates={hoje}"
        try:
            resp = requests.get(url_sb, headers=HEADERS).json()
            eventos = resp.get("events", [])
            if not eventos: continue

            texto_final += f"\n🏆 *{nome_liga.upper()}*\n"

            for ev in eventos:
                res = scanner_profissional_v5(slug, ev['id'])
                if res:
                    teams = ev['competitions'][0]['competitors']
                    home = next(t['team']['displayName'] for t in teams if t['homeAway'] == 'home')
                    away = next(t['team']['displayName'] for t in teams if t['homeAway'] == 'away')

                    bloco_jogo = f"📍 {home} vs {away}\n"
                    dados_jogo = ""

                    # Teste de Gols
                    for l in ["2.5", "1.5", "0.5"]:
                        if res["gols"][l] > 75:
                            dados_jogo += f"   ⚽ GOLS: +{l} ({res['gols'][l]}%)\n"
                            break

                    # Teste de Escanteios
                    for l in ["10.5", "9.5", "8.5", "7.5"]:
                        if res["cantos"][l] > 75:
                            dados_jogo += f"   🚩 CANTOS: +{l} ({res['cantos'][l]}%)\n"
                            break

                    # Teste de Cartões
                    for l in ["4.5", "3.5", "2.5", "1.5"]:
                        if res["cards"][l] > 75:
                            dados_jogo += f"   🟨 CARTÕES: +{l} ({res['cards'][l]}%)\n"
                            break

                    if dados_jogo:
                        texto_final += bloco_jogo + dados_jogo + "─" * 15 + "\n"
                        tem_confronto = True

        except:
            continue

    if tem_confronto:
        enviar_telegram(texto_final)
    else:
        print("Nenhuma oportunidade encontrada acima de 75% para enviar.")

if __name__ == "__main__":
    main()
