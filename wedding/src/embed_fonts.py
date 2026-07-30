import re, base64, urllib.request, os

SCRATCH = os.path.dirname(os.path.abspath(__file__))
css = open(os.path.join(SCRATCH, "gf.css"), encoding="utf-8").read()

blocks = re.findall(r"/\* (\S+) \*/\s*@font-face \{(.*?)\}", css, re.S)
out = []
seen = {}
proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({"https": proxy, "http": proxy}) if proxy else urllib.request.BaseHandler()
)

for subset, body in blocks:
    if subset not in ("arabic", "latin"):
        continue
    fam = re.search(r"font-family: '([^']+)'", body).group(1)
    style = re.search(r"font-style: (\S+);", body).group(1)
    weight = re.search(r"font-weight: ([^;]+);", body).group(1)
    url = re.search(r"src: url\((\S+?)\)", body).group(1)
    if style == "italic":
        continue
    if url in seen:
        b64 = seen[url]
    else:
        data = opener.open(url, timeout=60).read()
        b64 = base64.b64encode(data).decode()
        seen[url] = b64
        print(f"{fam} {weight} {style} {subset}: {len(data)//1024}KB")
    out.append(
        "@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:block;"
        "src:url(data:font/woff2;base64,%s) format('woff2');}" % (fam, style, weight, b64)
    )

open(os.path.join(SCRATCH, "fonts.css"), "w", encoding="utf-8").write("\n".join(out))
print("total css KB:", os.path.getsize(os.path.join(SCRATCH, "fonts.css")) // 1024)
