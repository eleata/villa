# Usage: python3 render_terminal.py IN.txt OUT.png [COLS=120] [FONT=Menlo]
# Render a captured terminal transcript (text file) to a PNG with a dark background and a monospace font.
import sys, textwrap
from PIL import Image, ImageDraw, ImageFont
src, dst = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 120
font = ImageFont.truetype(sys.argv[4] if len(sys.argv) > 4 else "/System/Library/Fonts/Menlo.ttc", 15)
lines = []
for raw in open(src, encoding="utf-8").read().splitlines():
    wrapped = textwrap.wrap(raw, cols, replace_whitespace=False, drop_whitespace=False, break_on_hyphens=False) or [""]
    lines += [(w, i > 0) for i, w in enumerate(wrapped)]
cw = font.getbbox("M")[2]; lh = 20; pad = 18
img = Image.new("RGB", (pad * 2 + cw * (cols + 2), pad * 2 + lh * len(lines)), (24, 26, 33))
d = ImageDraw.Draw(img)
for n, (text, cont) in enumerate(lines):
    color = (230, 230, 230)
    t = text.lstrip()
    if not cont and text.startswith("$ "): color = (126, 211, 135)
    elif not cont and text.startswith("#"): color = (140, 150, 170)
    elif t.startswith("[exit code") or t.startswith("[..."): color = (229, 192, 123)
    elif "error" in t.lower() or "Error" in t: color = (239, 112, 112)
    x = pad + (cw * 2 if cont else 0)
    d.text((x, pad + n * lh), text, font=font, fill=color)
img.save(dst, optimize=True)
print(dst, img.size)
