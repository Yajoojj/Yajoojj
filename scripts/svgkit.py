"""Primitivas compartilhadas pelos SVGs do perfil.

O texto vira <path> porque SVG carregado via <img> não acessa fontes externas:
assim a tipografia é a mesma em qualquer navegador.
"""
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = Path(__file__).parent / "fonts"

# A paleta vem da máscara de segmentação do GreenLeaf: folha em verde, mancha em vermelho.
BG = "#06070A"
PANEL = "#0C0F14"
LINE = "#222B36"
GRID = "#10141A"
RED = "#FF1F4B"
GREEN = "#35F28A"
AMBER = "#FFC53D"
TEXT = "#E8EEF2"
MUTED = "#8593A0"

REDUCED_MOTION = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def _num(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Face:
    def __init__(self, filename):
        self.font = TTFont(FONTS / filename)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm
        self.hmtx = self.font["hmtx"]

    def _name(self, ch):
        if ord(ch) not in self.cmap:
            raise ValueError(f"glifo ausente: {ch!r}")
        return self.cmap[ord(ch)]

    def width(self, text, size, spacing=0):
        scale = size / self.upm
        total = sum(self.hmtx[self._name(c)][0] * scale for c in text)
        return total + spacing * max(len(text) - 1, 0)

    def d(self, text, size, x=0, y=0, anchor="start", spacing=0):
        scale = size / self.upm
        width = self.width(text, size, spacing)
        pen_x = x - {"start": 0, "middle": width / 2, "end": width}[anchor]
        out = []
        for ch in text:
            name = self._name(ch)
            pen = SVGPathPen(self.glyphs, ntos=_num)
            self.glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, pen_x, y)))
            out.append(pen.getCommands())
            pen_x += self.hmtx[name][0] * scale + spacing
        return "".join(out)


DISPLAY = Face("ChakraPetch-Bold.ttf")
SEMI = Face("ChakraPetch-SemiBold.ttf")
MONO = Face("ShareTechMono-Regular.ttf")


def text(face, s, size, x, y, fill=TEXT, anchor="start", spacing=0, cls="", extra=""):
    attr = f' class="{cls}"' if cls else ""
    return f'<path{attr} fill="{fill}" {extra} d="{face.d(s, size, x, y, anchor, spacing)}"/>'


def chamfer(x, y, w, h, c=12):
    """Retângulo com os cantos superior esquerdo e inferior direito cortados."""
    return (
        f"M{x + c} {y}H{x + w}V{y + h - c}L{x + w - c} {y + h}H{x}V{y + c}Z"
    )


def grid_pattern(pid="grid", step=32):
    return (
        f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
        f'<path d="M{step} 0H0V{step}" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>'
    )


def svg(w, h, title, defs, css, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{title}"><title>{title}</title>'
        f"<defs>{defs}</defs><style>{css}{REDUCED_MOTION}</style>{body}</svg>"
    )
