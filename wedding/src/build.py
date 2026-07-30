import os
from urllib.parse import quote

S = os.path.dirname(os.path.abspath(__file__))
read = lambda p: open(os.path.join(S, p), encoding="utf-8").read()

GRAIN = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="220" height="220">'
    '<filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.82" numOctaves="4" '
    'stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/>'
    '<feComponentTransfer><feFuncA type="linear" slope="0.42"/></feComponentTransfer></filter>'
    '<rect width="220" height="220" filter="url(#g)" opacity="0.55"/></svg>'
)

html = read("invitation.template.html")

repl = {
    "{{FONTS}}": read("fonts.css"),
    "{{GRAIN}}": "data:image/svg+xml," + quote(GRAIN, safe=""),
    "{{TOP}}": read("ornaments/top.svg"),
    "{{BOTTOM}}": read("ornaments/bottom.svg"),
    "{{DIVIDER}}": read("ornaments/divider.svg"),
}
for k, v in repl.items():
    assert k in html, k
    html = html.replace(k, v)

out = os.path.join(S, "wedding-invitation.html")
open(out, "w", encoding="utf-8").write(html)
print(out, os.path.getsize(out) // 1024, "KB")
