"""Procedural watercolour-style botanical ornaments (deterministic)."""
import math
import os
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ornaments")
os.makedirs(OUT, exist_ok=True)

DEEP = "#3E5033"
MID = "#5E7548"
SAGE = "#7E9663"
LIGHT = "#9DB283"
PALE = "#BDCDA6"
GOLD = "#A9873F"
GOLD_L = "#CEB075"
GOLD_P = "#E6D6AE"
IVORY = "#FBF5E9"
BLUSH = "#F1E4D0"
BLUSH_D = "#D9C3A0"
BLUSH_S = "#C9AE86"

GREENS = [MID, SAGE, DEEP, LIGHT, SAGE, MID]


def f(x):
    return round(x, 2)


def bez(p0, p1, p2, p3, t):
    mt = 1 - t
    x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
    y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
    dx = 3 * mt**2 * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0]) + 3 * t**2 * (p3[0] - p2[0])
    dy = 3 * mt**2 * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1]) + 3 * t**2 * (p3[1] - p2[1])
    return (x, y), math.degrees(math.atan2(dy, dx))


# ------------------------------------------------------------------- leaves
def almond(L, W):
    return (f"M0 0 Q{f(L*.32)} {f(-W/2)} {f(L)} 0 Q{f(L*.32)} {f(W/2)} 0 0 Z")


def oval(L, W):
    """Eucalyptus-style rounded leaf on a short petiole."""
    s = L * .18
    return (f"M0 0 L{f(s)} 0 "
            f"C{f(s)} {f(-W*.58)} {f(L*.72)} {f(-W*.56)} {f(L)} 0 "
            f"C{f(L*.72)} {f(W*.56)} {f(s)} {f(W*.58)} {f(s)} 0 Z")


def willow(L, W):
    """Long, slightly curved olive leaf."""
    return (f"M0 0 C{f(L*.28)} {f(-W*.62)} {f(L*.72)} {f(-W*.52)} {f(L)} {f(-W*.10)} "
            f"C{f(L*.72)} {f(W*.44)} {f(L*.28)} {f(W*.52)} 0 0 Z")


SHAPES = {"almond": almond, "oval": oval, "willow": willow}


def branch(p0, p1, p2, p3, *, n=12, leaf=30, width=13, shape="almond",
           palette=None, stem=DEEP, spread=50, taper=.45, start=.08, end=1.0,
           sw=1.6, opacity=1.0, tip=True, vein=True, rnd=None, jit=10, sway=0):
    r = rnd or random.Random(3)
    pal = palette or GREENS
    fn = SHAPES[shape]
    out = [
        f'<path d="M{f(p0[0])} {f(p0[1])} C{f(p1[0])} {f(p1[1])} {f(p2[0])} {f(p2[1])} '
        f'{f(p3[0])} {f(p3[1])}" fill="none" stroke="{stem}" stroke-width="{sw}" '
        f'stroke-linecap="round" opacity="{opacity*.9}"/>'
    ]
    for i in range(n):
        t = start + (end - start) * (i / max(n - 1, 1))
        (x, y), ang = bez(p0, p1, p2, p3, t)
        side = 1 if i % 2 == 0 else -1
        a = ang + side * (spread + r.uniform(-jit, jit)) + sway
        sc = (1 - taper * t) * r.uniform(.82, 1.16)
        L, W = leaf * sc, width * sc
        col = pal[r.randrange(len(pal))]
        g = (f'<g transform="translate({f(x)} {f(y)}) rotate({f(a)})" opacity="{f(opacity*r.uniform(.86,1.0))}">'
             f'<path d="{fn(L, W)}" fill="{col}"/>')
        if vein:
            g += (f'<path d="M{f(L*.14)} 0 L{f(L*.82)} 0" stroke="{stem}" stroke-width=".7" '
                  f'opacity=".38" fill="none" stroke-linecap="round"/>')
        out.append(g + "</g>")
    if tip:
        (x, y), ang = bez(p0, p1, p2, p3, 1.0)
        L = leaf * (1 - taper) * .92
        out.append(f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)})">'
                   f'<path d="{fn(L, width*(1-taper)*.9)}" fill="{pal[0]}"/></g>')
    return "".join(out)


def berries(p0, p1, p2, p3, *, n=7, r0=4.4, color=GOLD_L, stroke=GOLD, rnd=None, spread=9):
    r = rnd or random.Random(11)
    out = []
    for i in range(n):
        t = .18 + .8 * (i / max(n - 1, 1))
        (x, y), ang = bez(p0, p1, p2, p3, t)
        a = math.radians(ang + 90)
        off = r.uniform(-spread, spread)
        cx, cy = x + math.cos(a) * off, y + math.sin(a) * off
        rr = r0 * r.uniform(.7, 1.2)
        out.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(rr)}" fill="{color}" '
                   f'stroke="{stroke}" stroke-width=".7" opacity=".92"/>')
    return "".join(out)


# -------------------------------------------------------------------- roses
def rose(P, cx, cy, r, rot=0, tone="blush"):
    grad = f"url(#{P}rose)" if tone == "blush" else f"url(#{P}rosei)"
    edge = BLUSH_S if tone == "blush" else BLUSH_D
    out = [f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)})">']
    # outer soft halo
    out.append(f'<circle r="{f(r*1.04)}" fill="{grad}" opacity=".75"/>')
    # petal rings
    for layer, (count, k) in enumerate(((7, 1.0), (5, .74), (4, .50))):
        rad = r * k
        for i in range(count):
            a = 360 / count * i + layer * 26
            out.append(
                f'<ellipse cx="{f(rad*.44)}" cy="0" rx="{f(rad*.54)}" ry="{f(rad*.42)}" '
                f'fill="{grad}" stroke="{edge}" stroke-width="{f(max(r*.028,.55))}" '
                f'opacity="{.96 - layer*.04}" transform="rotate({f(a)})"/>')
    out.append(f'<circle r="{f(r*.18)}" fill="{IVORY}" stroke="{edge}" stroke-width=".7"/>')
    sp = []
    for k in range(30):
        th = k * .40
        rr = r * .06 * math.exp(.14 * th)
        if rr > r * .32:
            break
        sp.append(f"{f(math.cos(th)*rr)} {f(math.sin(th)*rr)}")
    if len(sp) > 1:
        out.append(f'<path d="M{" L".join(sp)}" fill="none" stroke="{edge}" '
                   f'stroke-width="{f(max(r*.03,.6))}" opacity=".85"/>')
    out.append("</g>")
    return "".join(out)


def bud(cx, cy, r, rot=0, tone="blush"):
    fill = BLUSH if tone == "blush" else IVORY
    return (
        f'<g transform="translate({f(cx)} {f(cy)}) rotate({f(rot)})">'
        f'<path d="M0 0 C{f(-r*1.05)} {f(-r*.6)} {f(-r*.8)} {f(-r*2.1)} 0 {f(-r*2.5)} '
        f'C{f(r*.8)} {f(-r*2.1)} {f(r*1.05)} {f(-r*.6)} 0 0 Z" fill="{fill}" '
        f'stroke="{BLUSH_S}" stroke-width=".85"/>'
        f'<path d="M0 {f(-r*.25)} C{f(-r*.5)} {f(-r*1.0)} {f(-r*.4)} {f(-r*1.8)} 0 {f(-r*2.2)}" '
        f'fill="none" stroke="{BLUSH_S}" stroke-width=".75" opacity=".75"/>'
        f'<path d="M0 {f(r*.1)} C{f(-r*1.0)} {f(r*.3)} {f(-r*1.2)} {f(r*1.0)} {f(-r*.15)} {f(r*.8)}" fill="{MID}"/>'
        f'<path d="M0 {f(r*.1)} C{f(r*1.0)} {f(r*.3)} {f(r*1.2)} {f(r*1.0)} {f(r*.15)} {f(r*.8)}" fill="{MID}"/>'
        f'<path d="M0 {f(r*.4)} L0 {f(r*1.9)}" stroke="{DEEP}" stroke-width="1.2" stroke-linecap="round"/>'
        f'</g>')


# ------------------------------------------------------------ watercolour wash
def wash(P, blobs):
    out = [f'<g filter="url(#{P}blur)">']
    for cx, cy, rx, ry, rot, col, op in blobs:
        out.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" '
                   f'transform="rotate({f(rot)} {f(cx)} {f(cy)})" fill="{col}" opacity="{op}"/>')
    return "".join(out) + "</g>"


def defs(P, blur=13):
    return (
        "<defs>"
        f'<radialGradient id="{P}rose" cx="42%" cy="36%" r="72%">'
        f'<stop offset="0%" stop-color="#FFFCF6"/><stop offset="55%" stop-color="{BLUSH}"/>'
        f'<stop offset="100%" stop-color="{BLUSH_D}"/></radialGradient>'
        f'<radialGradient id="{P}rosei" cx="42%" cy="36%" r="72%">'
        f'<stop offset="0%" stop-color="#FFFFFC"/><stop offset="60%" stop-color="{IVORY}"/>'
        f'<stop offset="100%" stop-color="#E9DCC4"/></radialGradient>'
        f'<filter id="{P}blur" x="-40%" y="-40%" width="180%" height="180%">'
        f'<feGaussianBlur stdDeviation="{blur}"/></filter>'
        "</defs>")


# ------------------------------------------------------------- top garland
def top_half(P):
    """Left half of the crown: heavy in the corner, thinning to fine foliage at centre."""
    r = random.Random(21)
    p = [wash(P, [
        (130, 132, 138, 66, -14, "#CBD9B4", .50),
        (286, 104, 122, 48, -10, "#D7E2C2", .40),
        (58, 150, 80, 66, 16, "#C3D3AA", .42),
        (146, 128, 66, 48, 0, "#EFE2CB", .62),
        (248, 158, 48, 36, 0, "#EFE2CB", .50),
        (420, 80, 96, 40, -12, "#D2DEBB", .30),
        (150, 250, 44, 72, 6, "#CFDCB6", .28),
    ])]
    # main olive sweep — drops low at the outer edge, rises to the centre
    p.append(branch((-30, 168), (86, 42), (306, 26), (548, 44),
                    n=17, leaf=37, width=15, shape="willow", stem=DEEP,
                    spread=44, taper=.5, sw=1.9, rnd=r))
    # eucalyptus, rounder leaves, lower arc
    p.append(branch((-24, 222), (96, 122), (286, 98), (506, 96),
                    n=15, leaf=30, width=27, shape="oval", stem=MID,
                    palette=[SAGE, LIGHT, PALE, SAGE], spread=56, taper=.52,
                    sw=1.5, opacity=.97, rnd=r))
    # deep green filler through the corner cluster
    p.append(branch((16, 118), (132, 74), (256, 70), (396, 92),
                    n=12, leaf=26, width=11, shape="almond",
                    palette=[DEEP, MID, DEEP], stem=DEEP, spread=62, taper=.5,
                    sw=1.2, opacity=.9, rnd=r))
    # airy gold sprig arcing over the top
    p.append(branch((54, 176), (176, 62), (330, 30), (528, 68),
                    n=15, leaf=13, width=9, shape="oval",
                    palette=[GOLD_L, GOLD_P, GOLD_L], stem=GOLD, spread=64,
                    taper=.42, sw=1.0, opacity=.95, vein=False, rnd=r))
    # trailing vines
    p.append(branch((132, 172), (192, 236), (200, 292), (164, 340),
                    n=10, leaf=22, width=10, shape="oval",
                    palette=[LIGHT, PALE, SAGE], stem=MID, spread=66, taper=.55,
                    sw=1.2, opacity=.92, rnd=r))
    p.append(branch((28, 186), (40, 244), (26, 288), (50, 330),
                    n=8, leaf=18, width=8, shape="almond",
                    palette=[SAGE, LIGHT], stem=MID, spread=62, taper=.55,
                    sw=1.1, opacity=.85, rnd=r))
    p.append(berries((30, 130), (140, 82), (260, 76), (368, 104), n=8, r0=4.6, rnd=r))
    p.append(bud(206, 96, 13, -24))
    p.append(bud(80, 158, 12, 22))
    p.append(bud(318, 118, 10, -8))
    p.append(rose(P, 138, 134, 37, 12))
    p.append(rose(P, 244, 160, 27, -18))
    p.append(rose(P, 60, 110, 22, 34, tone="ivory"))
    p.append(rose(P, 330, 146, 19, 8, tone="ivory"))
    p.append(rose(P, 186, 188, 15, 40))
    p.append(rose(P, 404, 84, 12, -24))
    return "".join(p)


def top_garland():
    P = "t"
    half = top_half(P)
    return ('<svg class="orn orn-top" viewBox="0 0 1000 345" xmlns="http://www.w3.org/2000/svg" '
            'preserveAspectRatio="none" aria-hidden="true">' + defs(P) +
            f"<g>{half}</g><g transform=\"translate(1000 0) scale(-1 1)\">{half}</g></svg>")


# ---------------------------------------------------------- bottom garland
def bottom_half(P):
    """Left half of the footer swag: heavy in the corner, meeting at the centre."""
    r = random.Random(57)
    p = [wash(P, [
        (128, 176, 122, 54, 12, "#CBD9B4", .46),
        (272, 206, 112, 44, 4, "#D7E2C2", .38),
        (150, 168, 58, 42, 0, "#EFE2CB", .55),
        (48, 200, 74, 46, -16, "#C3D3AA", .36),
        (420, 224, 90, 34, 6, "#D2DEBB", .28),
    ])]
    p.append(branch((-30, 130), (96, 250), (310, 262), (548, 244),
                    n=16, leaf=33, width=14, shape="willow", stem=DEEP,
                    spread=46, taper=.5, sw=1.8, rnd=r))
    p.append(branch((-24, 82), (104, 178), (290, 200), (508, 200),
                    n=14, leaf=26, width=24, shape="oval",
                    palette=[SAGE, LIGHT, PALE, SAGE], stem=MID, spread=56,
                    taper=.52, sw=1.4, opacity=.96, rnd=r))
    p.append(branch((50, 126), (176, 236), (334, 264), (530, 228),
                    n=14, leaf=12, width=8, shape="oval",
                    palette=[GOLD_L, GOLD_P], stem=GOLD, spread=62, taper=.42,
                    sw=1.0, opacity=.95, vein=False, rnd=r))
    p.append(branch((16, 176), (130, 220), (254, 226), (392, 206),
                    n=11, leaf=22, width=9, shape="almond",
                    palette=[DEEP, MID], stem=DEEP, spread=64, taper=.5,
                    sw=1.1, opacity=.88, rnd=r))
    p.append(berries((26, 164), (138, 212), (258, 220), (366, 196), n=7, r0=4.2, rnd=r))
    p.append(bud(96, 202, 11, 162))
    p.append(bud(290, 224, 9, 196))
    p.append(rose(P, 150, 172, 29, -14))
    p.append(rose(P, 62, 148, 20, 22, tone="ivory"))
    p.append(rose(P, 250, 202, 17, 40))
    p.append(rose(P, 372, 226, 13, -30, tone="ivory"))
    return "".join(p)


def bottom_garland():
    P = "b"
    half = bottom_half(P)
    return ('<svg class="orn orn-bottom" viewBox="0 0 1000 290" xmlns="http://www.w3.org/2000/svg" '
            'preserveAspectRatio="none" aria-hidden="true">' + defs(P) +
            f"<g>{half}</g><g transform=\"translate(1000 0) scale(-1 1)\">{half}</g></svg>")


# ------------------------------------------------------------------ divider
def divider():
    P = "d"
    r = random.Random(5)
    p = [f'<svg class="divider" viewBox="0 0 460 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">',
         defs(P, blur=6)]
    p.append(wash(P, [(230, 34, 58, 20, 0, "#DDE6CB", .55)]))
    for x1, x2 in ((10, 156), (304, 450)):
        p.append(f'<path d="M{x1} 32 H{x2}" stroke="{GOLD}" stroke-width="1.2" opacity=".8"/>')
    p.append(f'<circle cx="166" cy="32" r="2.8" fill="{GOLD}" opacity=".9"/>')
    p.append(f'<circle cx="294" cy="32" r="2.8" fill="{GOLD}" opacity=".9"/>')
    p.append(branch((186, 38), (206, 14), (228, 10), (252, 16),
                    n=7, leaf=17, width=8, shape="oval",
                    palette=[SAGE, LIGHT, MID], stem=MID, spread=56, taper=.4,
                    sw=1.1, rnd=r))
    p.append(branch((274, 38), (254, 14), (232, 10), (208, 16),
                    n=7, leaf=17, width=8, shape="oval",
                    palette=[SAGE, LIGHT, MID], stem=MID, spread=-56, taper=.4,
                    sw=1.1, rnd=r))
    p.append(rose(P, 230, 34, 15, 10))
    p.append("</svg>")
    return "".join(p)


# -------------------------------------------------------------- corner sprig
def corner():
    P = "c"
    r = random.Random(91)
    p = ['<svg class="corner" viewBox="0 0 210 210" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">',
         defs(P, blur=8)]
    p.append(wash(P, [(72, 72, 62, 44, -45, "#CFDCB6", .45), (44, 44, 34, 26, -45, "#EFE2CB", .5)]))
    p.append(branch((26, 150), (24, 70), (70, 24), (150, 22),
                    n=12, leaf=24, width=11, shape="willow",
                    palette=[MID, SAGE, DEEP], stem=DEEP, spread=52, taper=.45,
                    sw=1.4, rnd=r))
    p.append(branch((40, 132), (46, 84), (84, 46), (132, 40),
                    n=9, leaf=17, width=15, shape="oval",
                    palette=[LIGHT, PALE, SAGE], stem=MID, spread=60, taper=.45,
                    sw=1.1, opacity=.92, rnd=r))
    p.append(branch((36, 118), (56, 78), (78, 56), (118, 36),
                    n=8, leaf=11, width=5, shape="almond",
                    palette=[GOLD_L, GOLD_P], stem=GOLD, spread=60, taper=.4,
                    sw=.9, vein=False, rnd=r))
    p.append(rose(P, 30, 150, 15, 20))
    p.append(rose(P, 152, 24, 12, -20, tone="ivory"))
    p.append(rose(P, 74, 74, 10, 40))
    p.append("</svg>")
    return "".join(p)


# ---------------------------------------------------------------- side vine
def side_vine():
    P = "s"
    r = random.Random(77)
    p = ['<svg class="vine" viewBox="0 0 120 420" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">',
         defs(P, blur=10)]
    p.append(wash(P, [(56, 200, 34, 150, 0, "#D2DEBB", .30)]))
    p.append(branch((60, 4), (94, 110), (30, 250), (66, 414),
                    n=16, leaf=22, width=10, shape="willow",
                    palette=[MID, SAGE, LIGHT], stem=MID, spread=58, taper=.25,
                    sw=1.2, opacity=.85, rnd=r))
    p.append(berries((60, 20), (92, 120), (32, 250), (66, 400), n=5, r0=3.4, rnd=r, spread=6))
    p.append("</svg>")
    return "".join(p)


assets = {
    "top.svg": top_garland(),
    "bottom.svg": bottom_garland(),
    "divider.svg": divider(),
    "corner.svg": corner(),
    "vine.svg": side_vine(),
}
for name, svg in assets.items():
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(svg)
    print(name, len(svg) // 1024, "KB")
