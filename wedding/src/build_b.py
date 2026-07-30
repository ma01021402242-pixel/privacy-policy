import os
from urllib.parse import quote
from build import GRAIN

S = os.path.dirname(os.path.abspath(__file__))
read = lambda p: open(os.path.join(S, p), encoding="utf-8").read()

html = read("invitation-b.template.html")
for k, v in {
    "{{FONTS}}": read("fonts.css"),
    "{{GRAIN}}": "data:image/svg+xml," + quote(GRAIN, safe=""),
    "{{CREST}}": read("ornaments_b/crest.svg"),
    "{{RULE}}": read("ornaments_b/rule.svg"),
    "{{SHOULDER}}": read("ornaments_b/shoulder.svg"),
    "{{FOOT}}": read("ornaments_b/foot.svg"),
}.items():
    assert k in html, k
    html = html.replace(k, v)

out = os.path.join(S, "wedding-invitation-b.html")
open(out, "w", encoding="utf-8").write(html)
print(out, os.path.getsize(out) // 1024, "KB")
