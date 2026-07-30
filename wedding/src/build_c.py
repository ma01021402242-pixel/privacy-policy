import os
from urllib.parse import quote
from build import GRAIN

S = os.path.dirname(os.path.abspath(__file__))
read = lambda p: open(os.path.join(S, p), encoding="utf-8").read()

med = read("ornaments_c/medallion.svg")
tip = read("ornaments_c/tip.svg")
html = read("invitation-c.template.html")

for k, v in {
    "{{FONTS}}": read("fonts.css"),
    "{{GRAIN}}": "data:image/svg+xml," + quote(GRAIN, safe=""),
    "{{TILE}}": "data:image/svg+xml," + quote(read("ornaments_c/tile.svg"), safe=""),
    "{{CARTOUCHE}}": read("ornaments_c/cartouche.svg"),
    "{{STARRULE}}": read("ornaments_c/starrule.svg"),
    "{{BAND}}": read("ornaments_c/band.svg"),
    "{{TIP_A}}": tip.replace('class="tip"', 'class="tip a"'),
    "{{TIP_B}}": tip.replace('class="tip"', 'class="tip b"'),
    **{f"{{{{MED_{p.upper()}}}}}": med.replace('class="med"', f'class="med {p}"')
       for p in ("tl", "tr", "bl", "br")},
}.items():
    assert k in html, k
    html = html.replace(k, v)

out = os.path.join(S, "wedding-invitation-c.html")
open(out, "w", encoding="utf-8").write(html)
print(out, os.path.getsize(out) // 1024, "KB")
