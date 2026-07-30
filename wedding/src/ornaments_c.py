"""Geometric (arabesque) ornaments for the third design — no florals."""
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ornaments_c")
os.makedirs(OUT, exist_ok=True)

GOLD = "#A8863C"
GOLD_L = "#CBAC69"
GOLD_P = "#E3D0A6"
WINE = "#6B2436"
WINE_L = "#8E3C4E"


def f(x):
    return round(x, 2)


def octagram(cx, cy, R, rot=0, inner=.541):
    """Rub el Hizb style eight-pointed star."""
    pts = []
    for i in range(16):
        r = R if i % 2 == 0 else R * inner
        a = math.radians(rot + i * 22.5)
        pts.append(f"{f(cx + r * math.cos(a))} {f(cy + r * math.sin(a))}")
    return "M" + " L".join(pts) + " Z"


def petal(cx, cy, ang, L, W):
    """Almond petal radiating from (cx, cy) at ang degrees."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    tx, ty = cx + ux * L, cy + uy * L
    c1 = (cx + ux * L * .3 + px * W, cy + uy * L * .3 + py * W)
    c2 = (cx + ux * L * .3 - px * W, cy + uy * L * .3 - py * W)
    return (f"M{f(cx)} {f(cy)} Q{f(c1[0])} {f(c1[1])} {f(tx)} {f(ty)} "
            f"Q{f(c2[0])} {f(c2[1])} {f(cx)} {f(cy)} Z")


# ------------------------------------------------------------------- tile
def tile(size=168):
    """Seamless girih-style watermark tile."""
    s = size
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}">',
         f'<g fill="none" stroke="{GOLD}" stroke-width="1.1">']
    p.append(f'<path d="{octagram(s/2, s/2, s*.27)}"/>')
    for cx, cy in ((0, 0), (s, 0), (0, s), (s, s)):
        p.append(f'<path d="{octagram(cx, cy, s*.27, 22.5)}"/>')
    p.append(f'<path d="M{s/2} 0 L{s} {s/2} L{s/2} {s} L0 {s/2} Z"/>')
    p.append(f'<circle cx="{s/2}" cy="{s/2}" r="{f(s*.115)}"/>')
    p.append("</g></svg>")
    return "".join(p)


# -------------------------------------------------------------- medallion
def medallion():
    """Quarter arabesque that sits in a corner of the frame."""
    p = ['<svg class="med" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">',
         f'<g fill="none" stroke="{GOLD}" stroke-linecap="round">']
    # sweeping arcs anchored on the corner
    p.append(f'<path d="M6 148 C6 66 66 6 148 6" stroke-width="1.6"/>')
    p.append(f'<path d="M6 176 C6 82 82 6 176 6" stroke-width=".9" opacity=".75"/>')
    p.append(f'<path d="M22 120 C22 66 66 22 120 22" stroke-width=".9" opacity=".8"/>')
    # leaf scrolls tucked inside the arc, pointing at the corner star
    for ang, sc in ((198, 1.0), (225, 1.28), (252, 1.0)):
        r = 94
        cx, cy = 100 + r * math.cos(math.radians(ang)), 100 + r * math.sin(math.radians(ang))
        p.append(f'<path d="{petal(f(cx), f(cy), ang - 180, 34 * sc, 12 * sc)}" '
                 f'fill="{GOLD_P}" stroke="{GOLD}" stroke-width=".9" opacity=".92"/>')
        dx, dy = math.cos(math.radians(ang)) * 12, math.sin(math.radians(ang)) * 12
        p.append(f'<circle cx="{f(cx + dx)}" cy="{f(cy + dy)}" r="2.6" fill="{GOLD}" '
                 f'stroke="none" opacity=".8"/>')
    p.append("</g>")
    p.append(f'<path d="{octagram(46, 46, 26)}" fill="{GOLD_P}" stroke="{GOLD}" '
             f'stroke-width="1.2" opacity=".95"/>')
    p.append(f'<path d="{octagram(46, 46, 13, 22.5)}" fill="none" stroke="{GOLD}" stroke-width=".9"/>')
    p.append(f'<circle cx="46" cy="46" r="4" fill="{WINE}" opacity=".8"/>')
    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------- cartouche
def cartouche(w=860, h=300):
    """Ogee-ended frame that holds the Qur'anic verse."""
    e, m = 62, 9          # tip length, inset between the two rules
    def shape(inset):
        x0, y0 = inset, inset
        x1, y1 = w - inset, h - inset
        ee = e - inset * .5
        return (f"M{f(x0)} {f((y0+y1)/2)} "
                f"C{f(x0+ee*.30)} {f(y0+(y1-y0)*.16)} {f(x0+ee*.66)} {f(y0)} {f(x0+ee)} {f(y0)} "
                f"L{f(x1-ee)} {f(y0)} "
                f"C{f(x1-ee*.66)} {f(y0)} {f(x1-ee*.30)} {f(y0+(y1-y0)*.16)} {f(x1)} {f((y0+y1)/2)} "
                f"C{f(x1-ee*.30)} {f(y1-(y1-y0)*.16)} {f(x1-ee*.66)} {f(y1)} {f(x1-ee)} {f(y1)} "
                f"L{f(x0+ee)} {f(y1)} "
                f"C{f(x0+ee*.66)} {f(y1)} {f(x0+ee*.30)} {f(y1-(y1-y0)*.16)} {f(x0)} {f((y0+y1)/2)} Z")
    p = [f'<svg class="cartouche" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
         'preserveAspectRatio="none" aria-hidden="true">']
    p.append(f'<path d="{shape(0)}" fill="rgba(255,252,244,.62)" stroke="{GOLD}" stroke-width="1.7"/>')
    p.append(f'<path d="{shape(m)}" fill="none" stroke="{GOLD_L}" stroke-width=".9" opacity=".9"/>')
    p.append("</svg>")
    return "".join(p)


def cartouche_tips(size=44):
    """The little stars that cap each end of the cartouche."""
    c = size / 2
    return (f'<svg class="tip" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
            f'<path d="{octagram(c, c, c*.86)}" fill="#FFFCF4" stroke="{GOLD}" stroke-width="1.4"/>'
            f'<path d="{octagram(c, c, c*.44, 22.5)}" fill="{GOLD_P}" stroke="{GOLD}" stroke-width=".8"/>'
            f'<circle cx="{c}" cy="{c}" r="{f(c*.13)}" fill="{WINE}"/></svg>')


# ----------------------------------------------------------------- divider
def star_rule(w=560):
    c = w / 2
    p = [f'<svg class="srule" viewBox="0 0 {w} 46" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">',
         f'<g stroke="{GOLD}" fill="none">']
    p.append(f'<path d="M8 23 H{f(c-52)}" stroke-width="1.2" opacity=".9"/>')
    p.append(f'<path d="M{f(c+52)} 23 H{w-8}" stroke-width="1.2" opacity=".9"/>')
    p.append(f'<path d="M20 17 H{f(c-64)}" stroke-width=".7" opacity=".55"/>')
    p.append(f'<path d="M{f(c+64)} 17 H{w-20}" stroke-width=".7" opacity=".55"/>')
    for dx in (-38, 38):
        p.append(f'<path d="{octagram(c+dx, 23, 9, 22.5)}" fill="{GOLD_P}" stroke-width=".8"/>')
    p.append("</g>")
    p.append(f'<path d="{octagram(c, 23, 21)}" fill="#FFFCF4" stroke="{GOLD}" stroke-width="1.3"/>')
    p.append(f'<path d="{octagram(c, 23, 10.5, 22.5)}" fill="{GOLD_P}" stroke="{GOLD}" stroke-width=".8"/>')
    p.append(f'<circle cx="{c}" cy="23" r="3" fill="{WINE}"/>')
    p.append("</svg>")
    return "".join(p)


def band(w=760):
    """Running geometric band used above the detail row."""
    p = [f'<svg class="band" viewBox="0 0 {w} 30" xmlns="http://www.w3.org/2000/svg" '
         'preserveAspectRatio="none" aria-hidden="true">',
         f'<g fill="none" stroke="{GOLD}" stroke-width="1">']
    step = 40
    n = int(w // step)
    for i in range(n):
        x = i * step + (w - n * step) / 2
        p.append(f'<path d="M{f(x)} 15 L{f(x+step/2)} 2 L{f(x+step)} 15 L{f(x+step/2)} 28 Z" '
                 f'stroke-width="1.2" opacity=".85"/>')
        p.append(f'<path d="{octagram(x+step/2, 15, 4.6, 22.5)}" fill="{GOLD_P}" stroke-width=".7"/>')
    p.append(f'<path d="M0 15 H{w}" stroke-width=".8" opacity=".6"/>')
    p.append("</g></svg>")
    return "".join(p)


assets = {
    "medallion.svg": medallion(),
    "cartouche.svg": cartouche(),
    "tip.svg": cartouche_tips(),
    "starrule.svg": star_rule(),
    "band.svg": band(),
    "tile.svg": tile(),
}
for name, svg in assets.items():
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(svg)
    print(name, len(svg), "B")
