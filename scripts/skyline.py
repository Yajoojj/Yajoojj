"""Desenha assets/skyline.svg: as contribuições dos últimos 12 meses como uma cidade.

Cada prédio é uma semana e cada janela acesa é uma contribuição.
Uso: GITHUB_TOKEN=... python scripts/skyline.py [usuario]
"""
import json
import os
import random
import sys
import urllib.request
from datetime import date
from pathlib import Path

from svgkit import BG, DISPLAY, GREEN, LINE, MONO, MUTED, RED, TEXT, grid_pattern, svg, text

OUT = Path(__file__).parent.parent / "assets" / "skyline.svg"
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{firstDay contributionDays{contributionCount}}}}}}"""
MONTHS = "JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ".split()


def fetch(login, token):
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [(w["firstDay"], sum(d["contributionCount"] for d in w["contributionDays"])) for w in calendar["weeks"]]
    return calendar["totalContributions"], weeks


def render(total, weeks):
    W, H = 1000, 292
    ground = H - 40
    left, right = 24, 24
    step = (W - left - right) / len(weeks)
    width = step - 3
    cols = 3
    win_w, win_h, row_h = (width - 6) / cols - 1.5, 4, 7
    max_rows = (ground - 96) // row_h
    peak = max(c for _, c in weeks) or 1
    unit = max(1, -(-peak // (cols * max_rows)))  # contribuições por janela

    rnd = random.Random(42)
    far = ""
    x = left - 10
    while x < W - right:
        w = rnd.randint(16, 44)
        far += f'<rect x="{x}" y="{ground - rnd.randint(16, 74)}" width="{w}" height="{H}" fill="#0E1219"/>'
        x += w - 2

    buildings, windows, twinkle, labels = "", "", "", ""
    last_month = None
    for i, (first_day, count) in enumerate(weeks):
        bx = left + i * step
        lit = -(-count // unit)
        rows = -(-lit // cols)
        height = max(rows, 2) * row_h + 10
        y = ground - height
        buildings += f'<rect x="{bx:.1f}" y="{y}" width="{width:.1f}" height="{height}" fill="#121821" stroke="{LINE}" stroke-width="1"/>'
        n = 0
        for row in range(rows):
            for col in range(cols):
                if n >= lit:
                    break
                wx, wy = bx + 3 + col * (win_w + 1.5), ground - 8 - row * row_h
                rect = f'x="{wx:.1f}" y="{wy}" width="{win_w:.1f}" height="{win_h}"'
                if rnd.random() < 0.07:
                    twinkle += f'<rect class="tw" style="animation-delay:-{rnd.uniform(0, 5):.2f}s" {rect} fill="{GREEN}"/>'
                else:
                    windows += f"<rect {rect}/>"
                n += 1
        if count == peak:
            buildings += f'<rect class="beacon" x="{bx + width / 2 - 1.5:.1f}" y="{y - 12}" width="3" height="12" fill="{RED}"/>'
        month = int(first_day[5:7])
        if month != last_month and i < len(weeks) - 2:
            labels += text(MONO, MONTHS[month - 1], 12, bx, H - 16, MUTED, spacing=.5)
            last_month = month

    css = """
.tw{animation:tw 5s steps(1) infinite}
@keyframes tw{20%{opacity:.15}26%{opacity:1}}
.beacon{animation:be 1.600s steps(1) infinite}
@keyframes be{50%{opacity:.2}}
.car{animation:car 11s linear infinite}
@keyframes car{from{transform:translateX(-60px)}to{transform:translateX(1060px)}}
"""
    legend = "1 JANELA = 1 CONTRIBUIÇÃO" if unit == 1 else f"1 JANELA = {unit} CONTRIBUIÇÕES"
    updated = date.today().strftime("%d/%m/%Y")
    body = f"""
<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>
{far}
<g class="car"><path d="M0 92.500H34" stroke="{RED}" stroke-opacity=".5"/><rect x="34" y="90" width="9" height="5" fill="{RED}"/></g>
{text(MONO, "// CIDADE DE COMMITS", 15, 24, 34, RED, spacing=1.500)}
{text(DISPLAY, f"{total}", 40, 24, 74, TEXT)}
{text(MONO, "CONTRIBUIÇÕES EM 12 MESES", 14, 24 + DISPLAY.width(f"{total}", 40) + 12, 74, MUTED, spacing=1)}
{text(MONO, "CADA PRÉDIO É UMA SEMANA", 14, W - 24, 34, TEXT, anchor="end", spacing=1)}
{text(MONO, legend, 14, W - 24, 54, GREEN, anchor="end", spacing=1)}
{text(MONO, f"ATUALIZADO EM {updated}", 12, W - 24, 74, MUTED, anchor="end", spacing=1)}
{buildings}
<g fill="{GREEN}">{windows}</g>{twinkle}
<path d="M0 {ground + .5}H{W}" stroke="{RED}"/>
{labels}
"""
    title = f"{total} contribuições nos últimos 12 meses, desenhadas como uma cidade: cada prédio é uma semana"
    OUT.write_text(svg(W, H, title, grid_pattern(), css, body), encoding="utf-8")
    print(f"skyline.svg: {OUT.stat().st_size / 1024:.1f} KB, {total} contribuições, pico semanal {peak}, 1 janela = {unit}")


if __name__ == "__main__":
    login = sys.argv[1] if len(sys.argv) > 1 else "Yajoojj"
    render(*fetch(login, os.environ["GITHUB_TOKEN"]))
