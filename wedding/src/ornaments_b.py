"""Ornaments for the second (minimal arch) design — tuned for a dark ground."""
import os
import random

from ornaments import (DEEP, MID, SAGE, LIGHT, PALE, GOLD, GOLD_L, GOLD_P,
                       branch, berries, rose, bud, wash, defs)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ornaments_b")
os.makedirs(OUT, exist_ok=True)

# lighter greens read better over the deep olive ground
BRIGHT = [SAGE, LIGHT, PALE, LIGHT, "#B7C9A0"]


def shoulder_spray():
    """Spray that sits on the arch's left shoulder and spills onto the dark ground."""
    P = "sa"
    r = random.Random(13)
    p = ['<svg class="spray spray-l" viewBox="0 0 460 420" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">',
         defs(P, blur=16)]
    p.append(wash(P, [
        (196, 150, 150, 78, -24, "#6E8556", .50),
        (110, 236, 92, 66, 20, "#5E7548", .42),
        (232, 128, 68, 48, 0, "#F0E3CE", .40),
        (300, 92, 74, 40, -30, "#7E9663", .34),
    ]))
    p.append(branch((30, 380), (78, 210), (216, 86), (426, 44),
                    n=17, leaf=42, width=17, shape="willow",
                    palette=BRIGHT, stem=MID, spread=44, taper=.44, sw=2.0, rnd=r))
    p.append(branch((16, 322), (96, 200), (214, 150), (392, 130),
                    n=14, leaf=34, width=30, shape="oval",
                    palette=[LIGHT, PALE, "#C6D6AF"], stem=SAGE, spread=56,
                    taper=.46, sw=1.6, rnd=r))
    p.append(branch((66, 336), (120, 230), (206, 178), (330, 168),
                    n=12, leaf=28, width=12, shape="almond",
                    palette=[MID, SAGE, DEEP], stem=DEEP, spread=64, taper=.5,
                    sw=1.3, opacity=.95, rnd=r))
    p.append(branch((92, 300), (170, 190), (280, 118), (420, 96),
                    n=14, leaf=15, width=10, shape="oval",
                    palette=[GOLD_L, GOLD_P], stem=GOLD, spread=62, taper=.42,
                    sw=1.1, vein=False, rnd=r))
    p.append(berries((54, 330), (128, 226), (236, 152), (368, 122), n=9, r0=5.2, rnd=r))
    p.append(bud(150, 210, 15, -34))
    p.append(bud(268, 116, 12, -18))
    p.append(rose(P, 108, 262, 42, 14))
    p.append(rose(P, 208, 168, 31, -20, tone="ivory"))
    p.append(rose(P, 60, 336, 24, 30, tone="ivory"))
    p.append(rose(P, 296, 108, 21, 8))
    p.append(rose(P, 158, 314, 17, -12))
    p.append("</svg>")
    return "".join(p)


def foot_spray():
    """Small counterweight sprig for the opposite bottom corner."""
    P = "sb"
    r = random.Random(41)
    p = ['<svg class="spray spray-r" viewBox="0 0 340 300" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">',
         defs(P, blur=13)]
    p.append(wash(P, [
        (150, 176, 108, 58, 16, "#6E8556", .44),
        (196, 150, 52, 38, 0, "#F0E3CE", .36),
    ]))
    p.append(branch((312, 42), (250, 150), (140, 214), (18, 246),
                    n=13, leaf=32, width=14, shape="willow",
                    palette=BRIGHT, stem=MID, spread=46, taper=.46, sw=1.7, rnd=r))
    p.append(branch((320, 96), (248, 178), (156, 226), (44, 240),
                    n=11, leaf=25, width=22, shape="oval",
                    palette=[LIGHT, PALE], stem=SAGE, spread=58, taper=.48,
                    sw=1.4, rnd=r))
    p.append(branch((296, 84), (230, 148), (156, 186), (68, 200),
                    n=10, leaf=13, width=9, shape="oval",
                    palette=[GOLD_L, GOLD_P], stem=GOLD, spread=60, taper=.42,
                    sw=1.0, vein=False, rnd=r))
    p.append(berries((300, 70), (232, 156), (140, 208), (52, 232), n=6, r0=4.4, rnd=r))
    p.append(bud(224, 168, 12, 150))
    p.append(rose(P, 176, 188, 27, -16))
    p.append(rose(P, 252, 136, 19, 26, tone="ivory"))
    p.append(rose(P, 108, 216, 15, 40))
    p.append("</svg>")
    return "".join(p)


def crest():
    """Tiny symmetric sprig that sits under the arch crown."""
    P = "cr"
    r = random.Random(9)
    half = (branch((0, 22), (26, 4), (56, 0), (86, 10),
                   n=7, leaf=17, width=8, shape="oval",
                   palette=[MID, SAGE, LIGHT], stem=MID, spread=56, taper=.42,
                   sw=1.1, rnd=r)
            + berries((6, 22), (30, 6), (58, 2), (84, 12), n=3, r0=3.2, rnd=r))
    return ('<svg class="crest" viewBox="0 0 200 46" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
            + defs(P, blur=5)
            + f'<g transform="translate(104 12)">{half}</g>'
            + f'<g transform="translate(96 12) scale(-1 1)">{half}</g>'
            + rose(P, 100, 24, 13, 8) + "</svg>")


def rule():
    """Hairline rule with a small gold lozenge at its centre."""
    return ('<svg class="rule" viewBox="0 0 400 20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
            f'<path d="M4 10 H172" stroke="{GOLD}" stroke-width="1.1" opacity=".85"/>'
            f'<path d="M228 10 H396" stroke="{GOLD}" stroke-width="1.1" opacity=".85"/>'
            f'<path d="M200 2 L208 10 L200 18 L192 10 Z" fill="{GOLD}" opacity=".95"/>'
            f'<circle cx="180" cy="10" r="2" fill="{GOLD}" opacity=".8"/>'
            f'<circle cx="220" cy="10" r="2" fill="{GOLD}" opacity=".8"/></svg>')


assets = {"shoulder.svg": shoulder_spray(), "foot.svg": foot_spray(),
          "crest.svg": crest(), "rule.svg": rule()}
for name, svg in assets.items():
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(svg)
    print(name, len(svg) // 1024, "KB")
