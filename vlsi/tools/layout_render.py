"""Render Microwind .MSK layouts (REC/TITLE records) as Microwind-style layout views.
Usage: python3 layout_render.py <msk> <out.png>
The geometry is read from the file; the window chrome is only styled to resemble Microwind."""
import re, sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

LAYERS = [  # draw order, face colour, alpha, legend name
    ("NW", "#c9b98a", 0.45, "N-well"),
    ("DP", "#e8a317", 0.85, "P+ diffusion"),
    ("DN", "#2eaa3c", 0.85, "N+ diffusion"),
    ("PO", "#d62828", 0.80, "Polysilicon"),
    ("ME", "#3a6ff0", 0.55, "Metal 1"),
    ("CO", "#111111", 1.00, "Contact"),
]


def parse(path):
    recs, titles, name = [], [], os.path.basename(path)
    for ln in open(path, encoding="latin-1").read().splitlines():
        m = re.match(r"REC\((-?\d+),(-?\d+),(-?\d+),(-?\d+),(\w+)\)", ln)
        if m:
            x, y, w, h = map(int, m.groups()[:4]); recs.append((x, y, w, h, m.group(5)))
        m = re.match(r"TITLE\s+(-?\d+)\s+(-?\d+)\s+#(.*)", ln)
        if m:
            titles.append((int(m.group(1)), int(m.group(2)), m.group(3).strip()))
    return recs, titles, name


def render(path, out):
    recs, titles, name = parse(path)
    xs = [r[0] for r in recs] + [r[0] + r[2] for r in recs] + [t[0] for t in titles]
    ys = [r[1] for r in recs] + [r[1] + r[3] for r in recs] + [t[1] for t in titles]
    x0, x1, y0, y1 = min(xs) - 8, max(xs) + 14, min(ys) - 8, max(ys) + 8
    W, H = x1 - x0, y1 - y0
    fw = 10.0
    lay_h = min(fw * 0.78 * H / W, 6.0)
    fig = plt.figure(figsize=(fw, lay_h + 1.35), dpi=150, facecolor="#d4d0c8")
    tot = lay_h + 1.35
    bar = fig.add_axes([0, 1 - 0.32 / tot, 1, 0.32 / tot]); bar.axis("off")
    bar.add_patch(Rectangle((0, 0), 1, 1, color="#0a246a"))
    bar.text(0.01, 0.5, "MICROWIND 3.1 - [%s]" % name, color="white", fontsize=9, va="center", weight="bold")
    men = fig.add_axes([0, 1 - 0.58 / tot, 1, 0.26 / tot]); men.axis("off")
    men.text(0.01, 0.5, "File   Edit   View   Simulate   Compile   Analysis   Help        Rules: cmos012.RUL   (120 nm, VDD = 1.2 V)",
             fontsize=7.5, va="center", color="#222")
    pal = fig.add_axes([0.005, 0.30 / tot, 0.19, 1 - 0.95 / tot]); pal.axis("off")
    pal.set_xlim(0, 1); pal.set_ylim(0, 1)
    pal.add_patch(Rectangle((0, 0), 1, 1, fc="#e6e3dc", ec="#808080"))
    pal.text(0.06, 0.96, "Palette", fontsize=8, weight="bold", va="top")
    for i, (_, col, a, nm) in enumerate(LAYERS):
        yy = 0.86 - i * 0.075
        pal.add_patch(Rectangle((0.07, yy), 0.16, 0.05, fc=col, alpha=max(a, 0.6), ec="#444", lw=0.6))
        pal.text(0.30, yy + 0.025, nm, fontsize=7, va="center")
    ax = fig.add_axes([0.21, 0.30 / tot, 0.78, lay_h / tot])
    ax.set_facecolor("white")
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal", adjustable="box")
    ax.set_xticks(range(int(x0 // 10 * 10), int(x1) + 1, 10)); ax.set_yticks(range(int(y0 // 10 * 10), int(y1) + 1, 10))
    ax.grid(True, color="#d8d8d8", lw=0.4); ax.tick_params(labelsize=5.5, length=2)
    for s in ax.spines.values(): s.set_color("#606060")
    for code, col, a, _ in LAYERS:
        for (x, y, w, h, l) in recs:
            if l != code: continue
            ax.add_patch(Rectangle((x, y), w, h, fc=col, alpha=a, ec=col if code != "CO" else "#000", lw=0.5))
            if code == "CO":
                ax.plot([x, x + w], [y, y + h], color="white", lw=0.4); ax.plot([x, x + w], [y + h, y], color="white", lw=0.4)
    for (x, y, t) in titles:
        ax.text(x, y, t, fontsize=8, color="#000", weight="bold",
                bbox=dict(boxstyle="round,pad=0.15", fc="#fff8b0", ec="#a08000", lw=0.5), va="bottom")
    st = fig.add_axes([0, 0, 1, 0.26 / tot]); st.axis("off")
    st.add_patch(Rectangle((0, 0), 1, 1, color="#d4d0c8"))
    st.text(0.01, 0.5, "Layout view | %d rectangles | lambda = 0.06 um | Select layer from palette" % len(recs), fontsize=7, va="center", color="#222")
    fig.savefig(out, facecolor=fig.get_facecolor()); plt.close(fig)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
