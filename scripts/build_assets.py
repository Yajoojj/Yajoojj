"""Gera os SVGs estáticos do perfil em assets/. Uso: python scripts/build_assets.py [pasta-de-icones]"""
import math
import random
import re
import sys
from pathlib import Path

from svgkit import (AMBER, BG, DISPLAY, GREEN, LINE, MONO, MUTED, PANEL, RED, SEMI, TEXT, chamfer,
                    grid_pattern, svg, text)

OUT = Path(__file__).parent.parent / "assets"
OUT.mkdir(exist_ok=True)


def save(name, content):
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"{name}: {len(content) / 1024:.1f} KB")


# ---------------------------------------------------------------- folha
def lobe_point(t, side, length, width):
    """Contorno de um lóbulo: t=0 na base, t=1 na ponta."""
    w = width * math.sin(math.pi * t ** 0.8) ** 1.15
    return side * w, -length * t


def rotate(p, angle, cx, cy):
    a = math.radians(angle)
    x, y = p
    return cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)


def leaf(cx, cy, seed=7):
    rnd = random.Random(seed)
    lobes = [(0, 200), (-38, 182), (38, 182), (-78, 152), (78, 152), (-120, 104), (120, 104)]
    outlines, veins, lesions, big = [], [], [], []
    for angle, length in lobes:
        width = length * 0.2
        pts = [lobe_point(i / 24, 1, length, width) for i in range(25)]
        pts += [lobe_point(i / 24, -1, length, width) for i in range(24, -1, -1)]
        abs_pts = [rotate(p, angle, cx, cy) for p in pts]
        outlines.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in abs_pts) + "Z")
        tip = rotate((0, -length), angle, cx, cy)
        veins.append(f"M{cx} {cy}L{tip[0]:.1f} {tip[1]:.1f}")
        for k in range(2, 9):
            t = k / 10
            for side in (1, -1):
                a = rotate((0, -length * t), angle, cx, cy)
                sx, sy = lobe_point(min(t + 0.09, 0.97), side, length, width)
                b = rotate((sx * 0.88, sy), angle, cx, cy)
                veins.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}")
        for _ in range(3 if length > 120 else 1):
            t = rnd.uniform(0.3, 0.85)
            lat = rnd.uniform(-0.55, 0.55) * width * math.sin(math.pi * t ** 0.8)
            c = rotate((lat, -length * t), angle, cx, cy)
            radius = rnd.uniform(4.5, 11)
            blob = []
            for j in range(9):
                ang = 2 * math.pi * j / 9
                r = radius * rnd.uniform(0.7, 1.2)
                blob.append(f"{c[0] + r * math.cos(ang):.1f} {c[1] + r * math.sin(ang):.1f}")
            lesions.append("M" + "L".join(blob) + "Z")
            big.append((radius, c))
    big.sort(key=lambda item: -item[0])
    return outlines, veins, lesions, big[:3]


def brackets(cx, cy, r):
    s = 6
    return "".join(
        f"M{cx + a * r} {cy + b * (r - s)}V{cy + b * r}H{cx + a * (r - s)}"
        for a in (-1, 1) for b in (-1, 1)
    )


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1000, 480
    cx, cy = 780, 318
    outlines, veins, lesions, big = leaf(cx, cy)
    rnd = random.Random(11)
    rain = "".join(
        f'<path class="r" d="M{rnd.randint(0, W + 80)} {rnd.randint(-60, -20)}l-7 {rnd.randint(22, 46)}" '
        f'style="animation-duration:{rnd.uniform(1.1, 2.4):.2f}s;animation-delay:-{rnd.uniform(0, 2.4):.2f}s"/>'
        for _ in range(38)
    )
    outline_d = "".join(outlines)
    veins_d = "".join(veins)
    lesions_d = "".join(lesions)
    stem = f"M{cx} {cy}C{cx + 6} {cy + 50} {cx + 24} {cy + 90} {cx + 46} {H}"
    bracket_d = "".join(brackets(c[0], c[1], r + 11) for r, c in big)

    yago = DISPLAY.d("YAGO", 118, 40, 172)
    kura = DISPLAY.d("KURASHIKI", 104, 40, 268)
    name = yago + kura

    css = f"""
.r{{stroke:{RED};stroke-width:1;fill:none;animation:rain 2s linear infinite}}
@keyframes rain{{to{{transform:translate(-84px,560px)}}}}
.type{{animation:type 1.6s steps(26) both}}
@keyframes type{{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}
.cur{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.split-a{{animation:sa 8s steps(1) infinite}}
.split-b{{animation:sb 8s steps(1) infinite}}
@keyframes sa{{0%,88%,100%{{transform:translate(-2.5px,0);clip-path:inset(0)}}89%{{transform:translate(-14px,0);clip-path:inset(8% 0 66% 0)}}91%{{transform:translate(10px,0);clip-path:inset(58% 0 18% 0)}}93%{{transform:translate(-8px,0);clip-path:inset(30% 0 44% 0)}}95%{{transform:translate(6px,0);clip-path:inset(76% 0 4% 0)}}}}
@keyframes sb{{0%,88%,100%{{transform:translate(2.5px,0);clip-path:inset(0)}}89%{{transform:translate(12px,0);clip-path:inset(40% 0 34% 0)}}91%{{transform:translate(-12px,0);clip-path:inset(4% 0 72% 0)}}93%{{transform:translate(9px,0);clip-path:inset(64% 0 12% 0)}}95%{{transform:translate(-6px,0);clip-path:inset(20% 0 58% 0)}}}}
.main{{animation:flick 8s steps(1) infinite}}
@keyframes flick{{0%,88%,96%,100%{{opacity:1}}89%,93%{{opacity:.55}}91%{{opacity:.85}}}}
.scanned{{animation:reveal 7s linear infinite}}
@keyframes reveal{{0%{{clip-path:inset(0 0 100% 0);opacity:1}}55%,90%{{clip-path:inset(0 0 0 0);opacity:1}}100%{{clip-path:inset(0 0 0 0);opacity:0}}}}
.beam{{opacity:0;animation:beam 7s linear infinite}}
@keyframes beam{{0%,10%{{opacity:0}}0%{{transform:translateY(0)}}11%,54%{{opacity:1}}55%{{transform:translateY(480px);opacity:0}}100%{{transform:translateY(480px);opacity:0}}}}
.hit{{animation:hit 7s linear infinite}}
@keyframes hit{{0%,50%{{opacity:0}}54%,90%{{opacity:1}}100%{{opacity:0}}}}
.st-a{{animation:sta 7s steps(1) infinite;opacity:0}}
@keyframes sta{{0%,54%{{opacity:1}}55%,100%{{opacity:0}}}}
.st-b{{animation:stb 7s steps(1) infinite}}
@keyframes stb{{0%,54%{{opacity:0}}55%,100%{{opacity:1}}}}
.pulse{{animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.35}}}}
"""
    defs = grid_pattern() + (
        f'<radialGradient id="gl" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{GREEN}" stop-opacity=".16"/>'
        f'<stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="rd" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{RED}" stop-opacity=".2"/>'
        f'<stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="bm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{GREEN}" stop-opacity=".16"/></linearGradient>'
        '<pattern id="hz" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="9" height="18" fill="{RED}"/></pattern>'
    )
    body = f"""
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
<ellipse cx="170" cy="400" rx="360" ry="230" fill="url(#rd)"/>
<ellipse cx="{cx}" cy="{cy - 60}" rx="300" ry="280" fill="url(#gl)"/>
<g opacity=".3">{rain}</g>

<path d="M0 0H{W}V38H0Z" fill="{PANEL}"/><path d="M0 38.500H{W}" stroke="{LINE}"/>
<g class="type">{text(MONO, "yago@vale-do-ribeira:~$ ./whoami", 16, 40, 25, GREEN)}</g>
<rect class="cur" x="326" y="12" width="9" height="16" fill="{GREEN}"/>
{text(MONO, "25.01°S 47.93°W", 15, W - 40, 25, MUTED, anchor="end", spacing=1)}

<path class="split-a" fill="{RED}" d="{name}"/>
<path class="split-b" fill="{GREEN}" d="{name}"/>
<path class="main" fill="{TEXT}" d="{name}"/>

<path d="{chamfer(40, 292, SEMI.width("DESENVOLVEDOR FULL-STACK", 21, .6) + 34, 42, 11)}" fill="{RED}"/>
{text(SEMI, "DESENVOLVEDOR FULL-STACK", 21, 56, 321, BG, spacing=.6)}
{text(SEMI, "Da rede neural à tela do celular.", 25, 40, 378, TEXT)}

<path d="{stem}" fill="none" stroke="{RED}" stroke-width="2.500" opacity=".7"/>
<path d="{outline_d}" fill="none" stroke="{GREEN}" stroke-opacity=".28" stroke-width="1"/>
<path d="{veins_d}" fill="none" stroke="{GREEN}" stroke-opacity=".08" stroke-width="1"/>
<g class="scanned">
  <rect width="{W}" height="{H}" fill="none"/>
  <path d="{outline_d}" fill="{GREEN}" fill-opacity=".14" stroke="{GREEN}" stroke-width="1.500"/>
  <path d="{veins_d}" fill="none" stroke="{GREEN}" stroke-opacity=".38" stroke-width="1"/>
  <path d="{lesions_d}" fill="{RED}" fill-opacity=".22" stroke="{RED}" stroke-opacity=".28" stroke-width="7"/>
  <path d="{lesions_d}" fill="{RED}" stroke="{AMBER}" stroke-width="1"/>
</g>
<path class="hit" d="{bracket_d}" fill="none" stroke="{TEXT}" stroke-width="1.500"/>
<g class="beam"><rect x="580" y="-70" width="400" height="70" fill="url(#bm)"/><path d="M580 0H980" stroke="{GREEN}" stroke-width="1.500"/></g>

<g transform="translate(868 58)">
  <path d="{chamfer(0, 0, 102, 60, 8)}" fill="{PANEL}" stroke="{LINE}"/>
  <rect x="10" y="12" width="9" height="9" fill="{GREEN}"/>{text(MONO, "FOLHA", 12, 25, 21, TEXT, spacing=.5)}
  <rect class="pulse" x="10" y="36" width="9" height="9" fill="{RED}"/>{text(MONO, "SUSPEITA", 12, 25, 45, TEXT, spacing=.5)}
</g>
<g class="st-a">{text(MONO, "VARREDURA...", 13, 590, 74, GREEN, spacing=1)}</g>
<g class="st-b">{text(MONO, "ÁREA DESTACADA", 13, 590, 74, RED, spacing=1)}</g>

<rect y="{H - 14}" width="{W}" height="14" fill="url(#hz)" opacity=".85"/>
"""
    save("hero.svg", svg(W, H, "Yago Kurashiki, desenvolvedor full-stack: da rede neural à tela do celular", defs, css, body))


# ---------------------------------------------------------------- comum aos painéis
def panel_head(W, label, title, right=None):
    out = text(MONO, label, 15, 24, 34, RED, spacing=1.5)
    out += text(DISPLAY, title, 40, 24, 74, TEXT, spacing=1)
    if right:
        out += text(MONO, right, 15, W - 24, 74, MUTED, anchor="end", spacing=1.5)
    return out


def background(W, H):
    return f'<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#grid)"/>'


def pct(seconds, cycle):
    return f"{max(0.0, min(100.0, seconds / cycle * 100)):.2f}%"


# ---------------------------------------------------------------- sobre
def ficha():
    W, H = 1000, 160
    fields = [
        ("ÁREA", "Full-stack", GREEN),
        ("FACULDADE", "FATEC Registro · DSM", GREEN),
        ("CLIENTE", "K9 Assessoria", RED),
    ]
    col_w = (W - 48) / 3
    body = background(W, H) + text(MONO, "// SOBRE", 15, 24, 34, RED, spacing=1.5)
    for i, (label, value, color) in enumerate(fields):
        x, y = 24 + i * col_w, 58
        body += f'<path d="{chamfer(x, y, col_w - 14, 78, 10)}" fill="{PANEL}" stroke="{LINE}"/>'
        body += f'<rect x="{x}" y="{y + 12}" width="3" height="54" fill="{color}"/>'
        body += text(MONO, label, 13, x + 18, y + 30, color, spacing=1.2)
        body += text(SEMI, value, 26, x + 18, y + 62, TEXT)
    title = "Sobre. Área: full-stack. Faculdade: FATEC Registro, DSM. Cliente: K9 Assessoria."
    save("ficha.svg", svg(W, H, title, grid_pattern(), "", body))


# ---------------------------------------------------------------- GreenLeaf
def greenleaf():
    """Fluxo em serpentina. O pulso corre por baixo das caixas, então some ao entrar e reaparece do outro lado."""
    W, H = 1000, 520
    node_w, node_h, gap = 280, 104, 52
    xs = [24, 24 + node_w + gap, 24 + 2 * (node_w + gap)]
    rows = [96, 96 + node_h + gap]
    tag = {"CELULAR": GREEN, "REDE": AMBER, "SERVIDOR": RED}
    nodes = [
        ("01", "FOTO", "Câmera ou galeria", "CELULAR", xs[0], rows[0]),
        ("02", "PREPARO", "1280 px, sem GPS nem EXIF", "CELULAR", xs[1], rows[0]),
        ("03", "POST /predict", "HTTPS, até 8 MB", "REDE", xs[2], rows[0]),
        ("04", "REDE NEURAL", "EfficientNet-B0 + HSV", "SERVIDOR", xs[2], rows[1]),
        ("05", "REGRAS", "Risco e gravidade", "SERVIDOR", xs[1], rows[1]),
        ("06", "DIAGNÓSTICO", "Linguagem simples", "CELULAR", xs[0], rows[1]),
    ]
    proc, travel, lead = 0.95, 0.55, 0.2
    cycle = lead + 6 * proc + 5 * travel + 1.0
    arrive = [lead + i * (proc + travel) for i in range(6)]

    # conectores: (x1, y1, x2, y2) da borda de uma caixa até a borda da seguinte
    y0, y1 = rows[0] + node_h / 2, rows[1] + node_h / 2
    xm = xs[2] + node_w / 2
    links = [
        (xs[0] + node_w, y0, xs[1], y0),
        (xs[1] + node_w, y0, xs[2], y0),
        (xm, rows[0] + node_h, xm, rows[1]),
        (xs[2], y1, xs[1] + node_w, y1),
        (xs[1], y1, xs[0] + node_w, y1),
    ]
    css = ""
    wires, packets = "", ""
    plen = 26
    for i, (ax, ay, bx, by) in enumerate(links):
        wires += f'<path d="M{ax} {ay}L{bx} {by}" stroke="{LINE}" stroke-width="2"/>'
        dx, dy = (bx > ax) - (bx < ax), (by > ay) - (by < ay)
        # começa inteiro escondido sob a caixa de origem e termina inteiro sob a de destino
        if dx:
            sx = ax - plen - 4 if dx > 0 else ax + 4
            ex = bx + 4 if dx > 0 else bx - plen - 4
            shape = f'<rect x="{sx}" y="{ay - 2}" width="{plen}" height="4" rx="2" fill="{GREEN}"/>'
            glow = f'<rect x="{sx - 6}" y="{ay - 6}" width="{plen + 12}" height="12" rx="6" fill="{GREEN}" opacity=".18"/>'
            move = f"translateX({ex - sx}px)"
        else:
            sy = ay - plen - 4
            ey = by + 4
            shape = f'<rect x="{ax - 2}" y="{sy}" width="4" height="{plen}" rx="2" fill="{GREEN}"/>'
            glow = f'<rect x="{ax - 6}" y="{sy - 6}" width="12" height="{plen + 12}" rx="6" fill="{GREEN}" opacity=".18"/>'
            move = f"translateY({ey - sy}px)"
        depart = arrive[i] + proc
        land = arrive[i + 1]
        css += (
            f"@keyframes k{i}{{0%,{pct(depart, cycle)}{{transform:none;animation-timing-function:cubic-bezier(.45,0,.55,1)}}"
            f"{pct(land, cycle)},100%{{transform:{move}}}}}.k{i}{{animation:k{i} {cycle:.2f}s infinite}}"
        )
        packets += f'<g class="k{i}">{glow}{shape}</g>'

    node_svg = ""
    for i, (num, title, sub, where, x, y) in enumerate(nodes):
        color = tag[where]
        a, done = arrive[i], arrive[i] + proc
        css += (
            f"@keyframes n{i}{{0%,{pct(a - 0.01, cycle)}{{opacity:0}}{pct(a + 0.12, cycle)},{pct(done, cycle)}{{opacity:1}}"
            f"{pct(done + 0.3, cycle)},94%{{opacity:.32}}100%{{opacity:0}}}}.n{i}{{opacity:0;animation:n{i} {cycle:.2f}s linear infinite}}"
        )
        shape = chamfer(x, y, node_w, node_h, 14)
        node_svg += (
            f'<path d="{shape}" fill="{PANEL}" stroke="{LINE}"/>'
            f'<path class="n{i}" d="{shape}" fill="{color}" fill-opacity=".1" stroke="{color}" stroke-width="1.5"/>'
            + text(MONO, num, 18, x + 18, y + 34, color)
            + text(MONO, where, 13, x + node_w - 16, y + 32, color, anchor="end", spacing=1)
            + text(SEMI, title, 27, x + 18, y + 66, TEXT)
            + text(MONO, sub, 16, x + 18, y + 90, MUTED)
        )

    metrics = [
        ("87,2%", "ACURÁCIA", "5 classes", .872),
        ("0,93", "AUC ROC", "bacteriose", .93),
        ("97,8%", "ESPECIFICIDADE", "bacteriose", .978),
        ("215 ms", "POR FOTO", "inferência em CPU", None),
    ]
    tile_w = 232
    metric_svg = ""
    for i, (value, label, note, fill) in enumerate(metrics):
        x, y = 24 + i * (tile_w + 16), 386
        metric_svg += text(DISPLAY, value, 42, x, y + 42, GREEN if fill else TEXT)
        metric_svg += text(MONO, label, 15, x, y + 66, TEXT, spacing=1)
        metric_svg += text(MONO, note, 14, x, y + 86, MUTED)
        metric_svg += f'<rect x="{x}" y="{y + 98}" width="{tile_w - 16}" height="4" fill="{LINE}"/>'
        if fill:
            metric_svg += f'<rect class="bar" x="{x}" y="{y + 98}" width="{(tile_w - 16) * fill:.1f}" height="4" fill="{GREEN}"/>'
    css += (".bar{transform-box:fill-box;transform-origin:0 0;animation:bar 1.6s cubic-bezier(.2,.7,.2,1) both}"
            "@keyframes bar{from{transform:scaleX(0)}}")

    body = (background(W, H) + panel_head(W, "// MISSÃO PRINCIPAL", "GREENLEAF", "DA FOTO AO DIAGNÓSTICO")
            + wires + packets + node_svg + metric_svg)
    title = ("Fluxo do GreenLeaf: foto, preparo no celular, POST /predict, rede neural EfficientNet-B0 com análise HSV, "
             "regras e diagnóstico. Acurácia de 87,2%, AUC de 0,93, especificidade de 97,8%, 215 ms por foto em CPU.")
    save("greenleaf.svg", svg(W, H, title, grid_pattern(), css, body))


# ---------------------------------------------------------------- stack
def stack(icon_dir):
    rows = [
        ("IA", GREEN, [("pytorch", "PyTorch", "Axios_Cassava_IA"), ("onnx", "ONNX Runtime", "Axios_Cassava_IA")]),
        ("BACK-END", RED, [("python", "Python", "at1-perceptron-knn"), ("fastapi", "FastAPI", "Axios_Cassava_IA"),
                           ("flask", "Flask", "no-meu-ritmo"), ("springboot", "Spring Boot", "estudando")]),
        ("FRONT-END", GREEN, [("typescript", "TypeScript", "Greenleaf-Mobile"), ("react", "React", "Greenleaf-Mobile"),
                              ("vite", "Vite", "Greenleaf-Mobile"), ("threedotjs", "Three.js", "Greenleaf-LP")]),
        ("DADOS E INFRA", RED, [("postgresql", "PostgreSQL", "bookflow-api"), ("supabase", "Supabase", "Greenleaf-Mobile"),
                                ("docker", "Docker", "Axios_Cassava_IA"), ("vercel", "Vercel", "Greenleaf-LP"),
                                ("render", "Render", "Axios_Cassava_IA")]),
    ]
    W, row_h = 1000, 76
    H = 56 + len(rows) * row_h + 16
    body = background(W, H) + text(MONO, "// ARSENAL", 15, 24, 34, RED, spacing=1.5)
    y, delay = 56, 0
    for label, color, items in rows:
        body += f'<path d="M24 {y + row_h - 6}H{W - 24}" stroke="{LINE}"/>'
        body += text(MONO, label, 15, 24, y + 37, color, spacing=1.2)
        for i, (slug, name, repo) in enumerate(items):
            d = re.search(r'd="([^"]+)"', (icon_dir / f"{slug}.svg").read_text(encoding="utf-8")).group(1)
            x = 170 + i * 163
            study = repo == "estudando"
            body += (f'<g class="ico" style="animation-delay:{delay:.2f}s"><g transform="translate({x} {y + 18}) scale(1.08)">'
                     f'<path fill="{AMBER if study else TEXT}" d="{d}"/></g></g>')
            body += text(MONO, name, 15, x + 33, y + 32, TEXT)
            body += text(MONO, repo.upper() if study else repo, 12, x + 33, y + 50, AMBER if study else GREEN, spacing=.3)
            delay += 0.28
        y += row_h
    css = """
.ico{animation:ico 5.600s linear infinite}
@keyframes ico{0%,8%{opacity:1}0%{opacity:.45}14%,100%{opacity:.72}}
"""
    title = "Stack e repositórios: " + "; ".join(f"{n} ({r})" for _, _, items in rows for _, n, r in items) + "."
    save("stack.svg", svg(W, H, title, grid_pattern(), css, body))


# ---------------------------------------------------------------- botões
def button(filename, label, color, title):
    width = int(MONO.width(label, 18, 1.2)) + 62
    h = 50
    body = (
        f'<path d="{chamfer(.5, .5, width - 1, h - 1, 10)}" fill="{BG}" stroke="{color}"/>'
        f'<rect class="p" x="16" y="{h / 2 - 4}" width="8" height="8" fill="{color}"/>'
        + text(MONO, label, 18, 36, h / 2 + 6, TEXT, spacing=1.2)
    )
    css = ".p{animation:p 1.800s steps(1) infinite}@keyframes p{50%{opacity:.25}}"
    save(filename, svg(width, h, title, "", css, body))


# ---------------------------------------------------------------- rodapé
def footer():
    W, H = 1000, 96
    defs = (
        '<pattern id="hz" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="9" height="18" fill="{RED}"/></pattern>'
    )
    css = ".c{animation:c 1s steps(1) infinite}@keyframes c{50%{opacity:0}}"
    label = "FIM DA TRANSMISSÃO · VALEU POR LER ATÉ AQUI"
    width = MONO.width(label, 18, 3)
    body = f"""
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="14" fill="url(#hz)" opacity=".85"/>
{text(MONO, label, 18, W / 2, 62, MUTED, anchor="middle", spacing=3)}
<rect class="c" x="{W / 2 + width / 2 + 8:.1f}" y="47" width="10" height="18" fill="{GREEN}"/>
"""
    save("footer.svg", svg(W, H, "Fim da transmissão", defs, css, body))


if __name__ == "__main__":
    icons = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "icons"
    hero()
    ficha()
    greenleaf()
    stack(icons)
    button("btn-linkedin.svg", "LINKEDIN", RED, "LinkedIn")
    button("btn-email.svg", "E-MAIL", RED, "E-mail")
    button("btn-lp.svg", "LANDING PAGE", GREEN, "Landing page do GreenLeaf")
    button("btn-app.svg", "ABRIR O APP", GREEN, "App GreenLeaf")
    button("btn-ia.svg", "API DA IA", GREEN, "Repositório da API de IA")
    button("btn-k9.svg", "VER O SITE", RED, "Site da K9 Assessoria")
    footer()
