"""Monta as vitrines (capturas reais em moldura HUD). Uso: python scripts/build_showcase.py <capturas> <prints>"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
OUT = ROOT.parent / "assets"
BG, LINE, RED, GREEN, TEXT, MUTED = "#06070A", "#222B36", "#FF1F4B", "#35F28A", "#E8EEF2", "#8593A0"
SCALE = 2  # exporta em 2x para continuar nítido em telas densas


def font(size):
    return ImageFont.truetype(str(ROOT / "fonts" / "ShareTechMono-Regular.ttf"), size * SCALE)


def fit(path, width, height, top=0):
    """Redimensiona pela largura e recorta a altura a partir de `top`."""
    image = Image.open(path).convert("RGB")
    ratio = width * SCALE / image.width
    image = image.resize((width * SCALE, round(image.height * ratio)), Image.LANCZOS)
    return image.crop((0, top * SCALE, width * SCALE, (top + height) * SCALE))


def base(width, height):
    canvas = Image.new("RGB", (width * SCALE, height * SCALE), BG)
    draw = ImageDraw.Draw(canvas)
    for x in range(0, width * SCALE, 32 * SCALE):
        draw.line([(x, 0), (x, height * SCALE)], fill="#10141A", width=SCALE)
    for y in range(0, height * SCALE, 32 * SCALE):
        draw.line([(0, y), (width * SCALE, y)], fill="#10141A", width=SCALE)
    return canvas, draw


def place(canvas, draw, image, x, y, color, label=None, sub=None):
    """Cola a captura com cantos de mira e etiqueta acima."""
    s = SCALE
    w, h = image.width // s, image.height // s
    canvas.paste(image, (x * s, y * s))
    draw.rectangle([x * s, y * s, (x + w) * s - 1, (y + h) * s - 1], outline=LINE, width=s)
    arm, off = 18, 6
    for cx, cy, dx, dy in ((x - off, y - off, 1, 1), (x + w + off, y - off, -1, 1),
                           (x - off, y + h + off, 1, -1), (x + w + off, y + h + off, -1, -1)):
        draw.line([(cx * s, cy * s), ((cx + dx * arm) * s, cy * s)], fill=color, width=2 * s)
        draw.line([(cx * s, cy * s), (cx * s, (cy + dy * arm) * s)], fill=color, width=2 * s)
    if label:
        draw.text((x * s, (y - 32) * s), label, font=font(15), fill=color)
    if sub:
        draw.text(((x + w) * s, (y - 32) * s), sub, font=font(13), fill=MUTED, anchor="ra")


def greenleaf(shots, prints):
    W, H = 1000, 470
    canvas, draw = base(W, H)
    top = 58
    screen_h = 380
    lp = fit(shots / "lp.png", 608, screen_h)
    place(canvas, draw, lp, 28, top, GREEN, "LANDING PAGE", "FOLHA 3D EM THREE.JS")
    phone_w = 148
    place(canvas, draw, fit(prints / "06-diagnostico-grave.png", phone_w, screen_h - 60, top=0), 664, top, RED, "DIAGNÓSTICO")
    place(canvas, draw, fit(prints / "07-diagnostico-area-destacada.png", phone_w, screen_h - 60, top=28), 826, top, RED, "ÁREA DESTACADA")
    draw.text((664 * SCALE, (top + screen_h - 40) * SCALE), "CAPTURAS REAIS DO APP", font=font(14), fill=TEXT)
    draw.text((664 * SCALE, (top + screen_h - 18) * SCALE), "PWA, MODO DEMONSTRAÇÃO", font=font(13), fill=MUTED)
    canvas.save(OUT / "greenleaf-telas.jpg", quality=86, optimize=True, progressive=True)


def k9(shots):
    W, H = 1000, 530
    canvas, draw = base(W, H)
    image = fit(shots / "k9.png", 944, 462)
    place(canvas, draw, image, 28, 48, RED, "// K9 ASSESSORIA", "LANDING PAGE EM PT E ES")
    canvas.save(OUT / "k9.jpg", quality=86, optimize=True, progressive=True)


if __name__ == "__main__":
    shots_dir, prints_dir = Path(sys.argv[1]), Path(sys.argv[2])
    greenleaf(shots_dir, prints_dir)
    k9(shots_dir)
    for name in ("greenleaf-telas.jpg", "k9.jpg"):
        print(name, (OUT / name).stat().st_size // 1024, "KB")
