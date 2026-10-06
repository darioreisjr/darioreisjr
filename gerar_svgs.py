"""
gerar_svgs.py
=============
Gera os quatro SVGs animados usados no README do perfil:

  github-contribution-animation.svg  grade de contribuições (dados reais da API do GitHub)
  terminal-card.svg                  avatar do GitHub convertido em arte ASCII
  info-card.svg                      cartão estilo neofetch
  code-card.svg                      editor de código com o objeto "dario"

Uso:
    pip install Pillow
    python gerar_svgs.py

O token é lido de GITHUB_TOKEN ou, se não existir, de `gh auth token`.
"""

import html
import json
import os
import subprocess
import sys
from datetime import date
from io import BytesIO
from urllib.request import Request, urlopen

# ─── CONFIG ──────────────────────────────────────────────────────────────────
USERNAME = "darioreisjr"
DISPLAY_NAME = "Dário Reis"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

C_ORANGE = "#ffa657"
C_BLUE = "#58a6ff"
C_GREEN = "#3fb950"
C_CYAN = "#22d3ee"
C_PURPLE = "#d2a8ff"
C_WHITE = "#c9d1d9"
C_DIM = "#30363d"
C_GRAY = "#7d8590"


def xe(s):
    return html.escape(str(s), quote=True)


def salvar(nome, svg):
    caminho = os.path.join(OUT_DIR, nome)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] {nome}  ({os.path.getsize(caminho) // 1024} KB)")


def chrome(largura, altura, titulo, grad_id):
    """Fundo, borda e barra de título estilo macOS compartilhados pelos cartões."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" '
        f'viewBox="0 0 {largura} {altura}" font-family="{FONT}">\n'
        f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/>'
        f"</linearGradient></defs>\n"
        f'<rect width="{largura}" height="{altura}" rx="12" fill="url(#{grad_id})"/>\n'
        f'<rect x="0.5" y="0.5" width="{largura - 1}" height="{altura - 1}" rx="12" fill="none" stroke="{C_DIM}"/>\n'
        f'<line x1="0" y1="30" x2="{largura}" y2="30" stroke="{C_DIM}"/>\n'
        f'<circle cx="20" cy="15" r="5" fill="#ff5f56"/>'
        f'<circle cx="36" cy="15" r="5" fill="#ffbd2e"/>'
        f'<circle cx="52" cy="15" r="5" fill="#27c93f"/>\n'
        f'<text x="{largura / 2:.1f}" y="19" fill="{C_GRAY}" font-size="12" text-anchor="middle">{xe(titulo)}</text>\n'
    )


# ─── DADOS DO GITHUB ─────────────────────────────────────────────────────────
def obter_token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    try:
        return subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        sys.exit("[ERR] Defina GITHUB_TOKEN ou faça login com `gh auth login`.")


QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date weekday contributionLevel } }
      }
    }
  }
}
"""


def buscar_dados():
    req = Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode(),
        headers={"Authorization": f"bearer {obter_token()}", "User-Agent": USERNAME},
    )
    resposta = json.loads(urlopen(req, timeout=30).read())
    if "errors" in resposta:
        sys.exit(f"[ERR] API do GitHub: {resposta['errors']}")
    return resposta["data"]["user"]


# ─── github-contribution-animation.svg ───────────────────────────────────────
NIVEIS = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}
CORES = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BRILHO = ["#21262d", "#3dffa0", "#57ffb0", "#8dffcc", "#c8ffe8"]
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def gerar_contribuicoes(calendario):
    semanas = calendario["weeks"]
    q, passo, gx, gy = 11, 14, 34, 28
    largura, altura = 850, 165
    dur_anim, pausa, inclinacao = 4.5, 2.5, 0.6
    total = dur_anim + pausa
    diag_max = (len(semanas) - 1) + 6 * inclinacao

    L = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}">',
        '<defs><filter id="cellglow" x="-70%" y="-70%" width="240%" height="240%">'
        '<feGaussianBlur stdDeviation="2" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        "</filter></defs>",
        f'<rect width="{largura}" height="{altura}" rx="16" fill="#0d1117" stroke="{C_DIM}" stroke-width="1"/>',
    ]

    # rótulos dos meses: na primeira semana em que cada mês aparece
    mes_anterior, x_anterior = None, -100
    for col, semana in enumerate(semanas):
        mes = date.fromisoformat(semana["contributionDays"][0]["date"]).month
        x = gx + col * passo
        if mes != mes_anterior and x - x_anterior >= 2 * passo:
            L.append(
                f'<text x="{x}" y="18" fill="#8b949e" font-size="10" '
                f'font-family="system-ui,sans-serif">{MESES[mes - 1]}</text>'
            )
            x_anterior = x
        mes_anterior = mes

    # rótulos dos dias (a semana do GitHub começa no domingo)
    for linha, rotulo in ((1, "Seg"), (3, "Qua"), (5, "Sex")):
        L.append(
            f'<text x="8" y="{gy + linha * passo + q - 1}" fill="#8b949e" font-size="9" '
            f'font-family="system-ui,sans-serif">{rotulo}</text>'
        )

    for col, semana in enumerate(semanas):
        for dia in semana["contributionDays"]:
            linha = dia["weekday"]
            nivel = NIVEIS[dia["contributionLevel"]]
            cor, brilho = CORES[nivel], BRILHO[nivel]
            x, y = gx + col * passo, gy + linha * passo

            # revelação em diagonal: quadrados da mesma diagonal aparecem juntos
            t0 = (col + linha * inclinacao) / diag_max * dur_anim / total
            t1 = min(t0 + 0.012, 0.97)
            t2 = min(t0 + 0.05, 0.99)
            filtro = ' filter="url(#cellglow)"' if nivel >= 3 else ""

            L.append(
                f'<rect x="{x}" y="{y}" width="{q}" height="{q}" rx="2" fill="{cor}" opacity="0"{filtro}>'
                f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{t0:.4f};{t1:.4f};1" '
                f'dur="{total}s" repeatCount="indefinite"/>'
            )
            if nivel > 0:
                L.append(
                    f'<animate attributeName="fill" values="{cor};{cor};{brilho};{cor}" '
                    f'keyTimes="0;{t0:.4f};{t1:.4f};{t2:.4f}" dur="{total}s" repeatCount="indefinite"/>'
                )
            L.append("</rect>")

    # rodapé: legenda
    y_rodape = gy + 7 * passo + 14
    L.append(
        f'<text x="{gx}" y="{y_rodape}" fill="#8b949e" font-size="11" font-family="system-ui,sans-serif">'
        f"Contribuições no último ano</text>"
    )
    x_leg = gx + (len(semanas) - 1) * passo + q - 5 * passo - 38
    L.append(
        f'<text x="{x_leg - 6}" y="{y_rodape}" fill="#8b949e" font-size="10" text-anchor="end" '
        f'font-family="system-ui,sans-serif">Menos</text>'
    )
    for i, cor in enumerate(CORES):
        L.append(f'<rect x="{x_leg + i * passo}" y="{y_rodape - 10}" width="{q}" height="{q}" rx="2" fill="{cor}"/>')
    L.append(
        f'<text x="{x_leg + 5 * passo + 4}" y="{y_rodape}" fill="#8b949e" font-size="10" '
        f'font-family="system-ui,sans-serif">Mais</text>'
    )

    L.append("</svg>")
    return "\n".join(L)


# ─── terminal-card.svg ───────────────────────────────────────────────────────
def gerar_retrato():
    try:
        from PIL import Image, ImageOps
    except ImportError:
        sys.exit("[ERR] Pillow não instalado. Rode: pip install Pillow")

    req = Request(
        f"https://avatars.githubusercontent.com/{USERNAME}?size=400",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    img = Image.open(BytesIO(urlopen(req, timeout=20).read())).convert("L")

    # rampa de densidade: pixel escuro = espaço, pixel claro = caractere denso
    rampa = "  `.-':=+*csS%#@"
    cols, lins = 100, 53
    img = ImageOps.autocontrast(img.resize((cols, lins), Image.LANCZOS), cutoff=2)
    px = list(img.getdata())
    linhas = [
        "".join(rampa[int(px[r * cols + c] / 255 * (len(rampa) - 1))] for c in range(cols))
        for r in range(lins)
    ]

    largura, alt_linha, y0, dur = 840, 15, 37, 0.11
    tx, tw = 20, 800
    y_linha_rodape = y0 + lins * alt_linha
    y_texto_rodape = y_linha_rodape + 19
    altura = y_linha_rodape + 43

    corpo = ""
    for i, linha in enumerate(linhas):
        inicio = i * dur
        y_topo = y0 + i * alt_linha
        corpo += (
            f'<clipPath id="r{i}"><rect x="{tx}" y="{y_topo}" height="{alt_linha}" width="0">'
            f'<animate attributeName="width" from="0" to="{tw}" begin="{inicio:.3f}s" dur="{dur}s" fill="freeze"/>'
            f"</rect></clipPath>\n"
            f'<g clip-path="url(#r{i})"><text xml:space="preserve" x="{tx}" y="{y_topo + 11.1:.1f}" '
            f'fill="{C_WHITE}" font-size="12.9" textLength="{tw}" lengthAdjust="spacing">{xe(linha)}</text></g>\n'
            f'<rect y="{y_topo + 1}" width="8" height="13" fill="{C_WHITE}" opacity="0">'
            f'<animate attributeName="x" from="{tx}" to="{tx + tw}" begin="{inicio:.3f}s" dur="{dur}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{inicio:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{inicio + dur:.3f}s"/>'
            f"</rect>\n"
        )

    prompt = f"{USERNAME}@github:~$ whoami "
    cursor_x = tx + (len(prompt) + len(DISPLAY_NAME) + 1) * 7.83
    return (
        chrome(largura, altura, f"{USERNAME}@github: ~$ ./retrato.sh", "bg")
        + corpo
        + f'<line x1="0" y1="{y_linha_rodape}" x2="{largura}" y2="{y_linha_rodape}" stroke="{C_DIM}"/>\n'
        f'<text xml:space="preserve" x="{tx}" y="{y_texto_rodape}" fill="{C_GRAY}" font-size="13">{xe(prompt)}'
        f'<tspan fill="{C_WHITE}">{xe(DISPLAY_NAME)}</tspan></text>\n'
        f'<rect x="{cursor_x:.0f}" y="{y_texto_rodape - 12}" width="8" height="14" fill="{C_WHITE}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>'
        f"</rect>\n</svg>"
    )


# ─── info-card.svg ───────────────────────────────────────────────────────────
def gerar_info():
    itens = [
        ("cabecalho",),
        ("secao", "— Sobre"),
        ("campo", "Cargo", "Desenvolvedor de Software"),
        ("campo", "Foco", "Front-end · React, Next.js, TypeScript"),
        ("campo", "Atual", "Desenvolvedor Front-end @ ProBrain"),
        ("campo", "Comunidade", "Fundador & Líder Técnico @cafebugado"),
        ("campo", "Local", "São Paulo, Brasil"),
        ("secao", "— Stack"),
        ("campo", "Frontend", "React, Next.js, TypeScript"),
        ("campo", "Backend", "Node.js, NestJS"),
        ("campo", "Dados", "PostgreSQL, Supabase, Prisma"),
        ("campo", "DevOps", "GitHub Actions, Vercel"),
        ("secao", "— Destaques"),
        ("marcador", "Arquitetura Front-end e Design Systems"),
        ("marcador", "Performance, acessibilidade e qualidade"),
        ("marcador", "Experiência Full Stack em projetos reais"),
        ("marcador", "Aplicações próprias em produção"),
    ]

    largura, alt_linha, dur, passo = 480, 20.5, 0.4, 0.06
    y, t, partes = 60.0, 0.15, []

    def grupo(conteudo):
        return (
            f'<g opacity="0" transform="translate(0,5)">{conteudo}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="{dur}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{t:.2f}s" dur="{dur}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>'
        )

    def regua(x1):
        return (
            f'<line x1="{x1:.0f}" y1="{y - 4:.1f}" x2="{largura - 20}" y2="{y - 4:.1f}" '
            f'stroke="{C_DIM}" stroke-opacity="0.8"/>'
        )

    for item in itens:
        tipo = item[0]
        if tipo == "cabecalho":
            partes.append(grupo(
                f'<text x="20" y="{y}" font-size="14" font-weight="700">'
                f'<tspan fill="{C_GREEN}">{xe(USERNAME)}</tspan><tspan fill="{C_GRAY}">@</tspan>'
                f'<tspan fill="{C_CYAN}">github</tspan></text>'
                + regua(20 + (len(USERNAME) + 8) * 8.6)
            ))
            y += alt_linha * 1.1
            t += passo
        elif tipo == "secao":
            partes.append(grupo(
                f'<text x="20" y="{y}" fill="{C_BLUE}" font-size="12.5" font-weight="700">{xe(item[1])}</text>'
                + regua(28 + len(item[1]) * 7.6)
            ))
            y += alt_linha * 1.5
            t += passo * 2
        elif tipo == "campo":
            partes.append(grupo(
                f'<text x="20" y="{y}" fill="{C_ORANGE}" font-size="12.5" font-weight="700">{xe(item[1])}</text>'
                f'<text x="112" y="{y}" fill="{C_WHITE}" font-size="12.5">{xe(item[2])}</text>'
            ))
            y += alt_linha
            t += passo
        else:
            partes.append(grupo(
                f'<circle cx="23" cy="{y - 4:.1f}" r="2.5" fill="{C_GREEN}"/>'
                f'<text x="34" y="{y}" fill="{C_WHITE}" font-size="12.5">{xe(item[1])}</text>'
            ))
            y += alt_linha
            t += passo

    altura = max(420, int(y) + 14)
    return chrome(largura, altura, f"{USERNAME}@github: ~$ neofetch", "ibg") + "\n".join(partes) + "\n</svg>"


# ─── code-card.svg ───────────────────────────────────────────────────────────
def gerar_codigo():
    K, P, S, T = C_PURPLE, "#79c0ff", "#a5d6ff", C_WHITE  # palavra-chave, propriedade, string, texto

    def prop(nome, valor, cor=S):
        return [("  ", T), (nome, P), (": ", T), (valor, cor), (",", T)]

    def item(valor):
        return [("    ", T), (valor, S), (",", T)]

    linhas = [
        [("const", K), (" dario", C_ORANGE), (" = {", T)],
        prop("cargo", '"Desenvolvedor de Software"'),
        prop("atuacao", '"Front-end"'),
        prop("empresa", '"ProBrain"'),
        prop("comunidade", '"Café Bugado · Fundador & Líder Técnico"'),
        [("  ", T), ("focoAtual", P), (": [", T)],
        item('"Arquitetura Front-end"'),
        item('"Design Systems"'),
        item('"Performance Web"'),
        item('"Engenharia de Software"'),
        [("  ],", T)],
        [("  ", T), ("aprendendo", P), (": [", T)],
        item('"Arquitetura de Software"'),
        item('"Aplicações de IA"'),
        item('"Cloud Fundamentals"'),
        [("  ],", T)],
        prop("curiosidade", '"Transformo café em código limpo ☕"'),
        [("};", T)],
    ]

    largura, alt_linha, y0, dur = 640, 21, 58, 0.35
    altura = y0 + len(linhas) * alt_linha + 12
    corpo = ""
    for i, tokens in enumerate(linhas):
        y = y0 + i * alt_linha
        inicio = 0.3 + i * dur
        spans = "".join(f'<tspan fill="{cor}">{xe(txt)}</tspan>' for txt, cor in tokens)
        corpo += (
            f'<text x="34" y="{y}" fill="#484f58" font-size="12" text-anchor="end">{i + 1}</text>\n'
            f'<clipPath id="c{i}"><rect x="48" y="{y - 15}" height="{alt_linha}" width="0">'
            f'<animate attributeName="width" from="0" to="{largura - 60}" begin="{inicio:.2f}s" dur="{dur}s" fill="freeze"/>'
            f"</rect></clipPath>\n"
            f'<text xml:space="preserve" x="48" y="{y}" font-size="13" clip-path="url(#c{i})">{spans}</text>\n'
        )
    return chrome(largura, altura, "dario.ts", "cbg") + corpo + "</svg>"


if __name__ == "__main__":
    usuario = buscar_dados()
    salvar(
        "github-contribution-animation.svg",
        gerar_contribuicoes(usuario["contributionsCollection"]["contributionCalendar"]),
    )
    salvar("terminal-card.svg", gerar_retrato())
    salvar("info-card.svg", gerar_info())
    salvar("code-card.svg", gerar_codigo())
