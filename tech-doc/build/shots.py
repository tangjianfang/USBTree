import os, re, subprocess, glob
# 可选：把每篇 HTML 里最大的 SVG 用 headless Chrome 截成 PNG，供人工看图。
# 截图写到 TECH_DOC_SHOTS（默认 /tmp/tech-doc-shots），不写入仓库。
_HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(_HERE))
out = os.environ.get("TECH_DOC_SHOTS") or "/tmp/tech-doc-shots"
os.makedirs(out, exist_ok=True)
for f in sorted(glob.glob("*.html")):
    n = os.path.basename(f)[:-5]
    h = open(f, encoding="utf-8").read()
    svg = max(re.findall(r"<svg.*?</svg>", h, flags=re.S), key=len)
    vb = re.search(r'viewBox="([\d\.\- ]+)"', svg)
    w, hh = [float(x) for x in vb.group(1).split()[2:]]
    tmp = f"/tmp/d_{n}.html"
    open(tmp, "w", encoding="utf-8").write(
        f'<html><body style="margin:0;background:#fff">{svg}</body></html>'
    )
    shot = os.path.join(out, f"diagram-{n}.png")
    subprocess.run(
        [
            "google-chrome",
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size={int(w)+20},{int(hh)+20}",
            f"--screenshot={shot}",
            f"file://{tmp}",
        ],
        capture_output=True,
        timeout=60,
    )
    print(n, int(w), int(hh), shot)
