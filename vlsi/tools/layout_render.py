"""Render Microwind .MSK layouts (REC/TITLE records) in a Microwind 3.1 style window (black canvas, palette panel).
Usage: python3 layout_render.py <msk> <out.png>
Geometry comes from the file; the window chrome is only styled to resemble Microwind."""
import re, sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

PX_W, PX_H = 1600, 890
# draw order: layer code, colour, alpha, hatch
LAYERS = [("NW", "#0e2e0e", 0.55, None), ("DP", "#a08a20", 0.90, None), ("DN", "#2e8b2e", 0.95, None),
          ("PO", "#ff2d1a", 0.85, None), ("ME", "#1010ff", 0.85, None), ("CO", "#e4e4ff", 1.0, None)]
PALETTE = [("Options", "#fff7a8"), ("Metal 6", "#909090"), ("Metal 5", "#3b3b9a"), ("Metal 4", "#4a9a00"), ("Metal 3", "#35358f"),
           ("Metal 2", "#0000c0"), ("Metal 1", "#2a52ff"), ("Polysilicon 2", "#ff0000"), ("Contact", "#d8d8d8"),
           ("Polysilicon", "#ff0000"), ("P+ Diffusion", "#808000"), ("N+ Diffusion", "#008000"), ("N Well", "#b5cdb5")]


def parse(path):
    recs, titles = [], []
    for ln in open(path, encoding="latin-1").read().splitlines():
        m = re.match(r"REC\((-?\d+),(-?\d+),(-?\d+),(-?\d+),(\w+)\)", ln)
        if m:
            x, y, w, h = map(int, m.groups()[:4]); recs.append((x, y, w, h, m.group(5)))
        m = re.match(r"TITLE\s+(-?\d+)\s+(-?\d+)\s+#(.*)", ln)
        if m:
            titles.append((int(m.group(1)), int(m.group(2)), m.group(3).strip()))
    return recs, titles


def render(path, out):
    recs, titles = parse(path)
    name = os.path.splitext(os.path.basename(path))[0]
    fig = plt.figure(figsize=(PX_W / 100, PX_H / 100), dpi=100, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PX_W); ax.set_ylim(PX_H, 0); ax.axis("off")
    R = lambda x, y, w, h, **k: ax.add_patch(Rectangle((x, y), w, h, **k))
    cy0, cy1 = 76, 833
    R(0, cy0, PX_W, cy1 - cy0, fc="black", ec="none")
    xs = [r[0] for r in recs] + [r[0] + r[2] for r in recs] + [t[0] for t in titles]
    ys = [r[1] for r in recs] + [r[1] + r[3] for r in recs] + [t[1] for t in titles]
    lx0, lx1, ly0, ly1 = min(xs) - 4, max(xs) + 6, min(ys) - 4, max(ys) + 6
    s = min((1380 - 60) / (lx1 - lx0), (cy1 - cy0 - 90) / (ly1 - ly0))
    ox = 60 + ((1380 - 60) - s * (lx1 - lx0)) / 2 - lx0 * s
    oy = cy1 - 40 - ((cy1 - cy0 - 90) - s * (ly1 - ly0)) / 2 + ly0 * s
    P = lambda x, y: (ox + x * s, oy - y * s)
    gx = [v for v in (ox + k * 5 * s for k in range(-80, 400)) if 4 < v < 1596]
    gy = [v for v in (oy - k * 5 * s for k in range(-80, 400)) if cy0 + 4 < v < cy1 - 4]
    ax.scatter([a for a in gx for _ in gy], [b for _ in gx for b in gy], s=1.2, c="#9a9a9a", marker="s", linewidths=0, zorder=1)
    for code, col, a, hatch in LAYERS:
        for (x, y, w, h, l) in recs:
            if l != code: continue
            px, py = P(x, y + h)
            R(px, py, w * s, h * s, fc=col, alpha=a, ec="#2a8a2a" if code == "NW" else "none", lw=1.2, hatch=hatch, zorder=2)
            if code == "CO":
                ax.plot([px, px + w * s], [py, py + h * s], color="#303080", lw=0.9, zorder=3)
                ax.plot([px, px + w * s], [py + h * s, py], color="#303080", lw=0.9, zorder=3)
    for (x, y, t) in titles:
        px, py = P(x, y); ax.text(px, py, t, color="white", fontsize=9, va="bottom", zorder=5)
    ax.text(10, 92, "5 lambda", color="white", fontsize=7.5, va="center")
    ax.plot([6, 6 + 5 * s], [106, 106], color="white", lw=1.5); ax.text(10, 118, "%.3fµm" % (5 * 0.06), color="white", fontsize=7.5, va="center")
    R(0, 0, PX_W, 24, fc="white"); R(2, 4, 14, 14, fc="#222", ec="none")
    ax.text(24, 12, "Microwind Version 3.1 - %s" % name, fontsize=9, va="center", color="#555")
    ax.text(1475, 12, "—", fontsize=10, va="center", color="#555"); ax.text(1520, 12, "▢", fontsize=10, va="center", color="#555")
    ax.text(1568, 12, "✕", fontsize=10, va="center", color="#555")
    R(0, 24, PX_W, 21, fc="white")
    for lab, x in (("File", 7), ("View", 41), ("Edit", 81), ("Simulate", 117), ("Compile", 179), ("Analysis", 241), ("Help", 300)):
        ax.text(x, 34, lab, fontsize=8.5, va="center", color="#333")
    R(0, 45, PX_W, 31, fc="#c8c8c8", ec="none")
    icol = ["#e8b300", "#2d6bd0", "#2db02d", "#222", "#2db02d", "#e8b300", "#555", "#555", "#d4a000", "#d33", "#2db02d", "#222",
            "#2d6bd0", "#2db02d", "#2d6bd0", "#222", "#d4a000", "#d33", "#2db02d", "#2d6bd0"]
    for i, c in enumerate(icol):
        R(8 + i * 27 + (12 if i > 7 else 0) + (14 if i > 13 else 0), 54, 14, 14, fc=c, ec="none")
    px0, py0 = 1466, 94
    R(px0, py0, 132, 421, fc="#f1f1f1", ec="#b0b0b0", lw=1, zorder=6)
    R(px0 + 6, py0 + 5, 14, 14, fc="#222", zorder=7); ax.text(px0 + 26, py0 + 12, "Palette", fontsize=8.5, va="center", zorder=7)
    ax.text(px0 + 116, py0 + 12, "✕", fontsize=9, va="center", zorder=7)
    for i in range(5): R(px0 + 6 + i * 24, py0 + 34, 14, 14, fc="#1aa0d0", zorder=7)
    for i in range(5): R(px0 + 6 + i * 24, py0 + 60, 14, 14, fc="#1a6fd0", zorder=7)
    for i in range(5): R(px0 + 6 + i * 20, py0 + 92, 12, 12, fc="#1a50c0", zorder=7)
    for i, (nm, col) in enumerate(PALETTE):
        yy = 211 + i * 23
        R(px0 + 1, yy, 98, 21, fc="#f6f6f6", ec="#c8c8c8", lw=0.8, zorder=7)
        ax.text(px0 + 9, yy + 11, nm, fontsize=7.5, va="center", zorder=8, color="#c00000" if nm == "Polysilicon" else "#222")
        R(px0 + 72, yy + 4, 14, 14, fc=col, ec="#999", lw=0.6, zorder=8)
    R(px0 + 1, 211 + 11 * 23, 98, 21, fc="none", ec="#000", lw=1.0, zorder=9)
    R(0, cy1, PX_W, 21, fc="#f0f0f0")
    ax.text(3, cy1 + 10, "Show palette menu...", fontsize=8, va="center"); ax.plot([470, 470], [cy1, cy1 + 21], color="#aaa", lw=0.8)
    ax.text(474, cy1 + 10, "Hit %d" % len(recs), fontsize=8, va="center"); ax.plot([627, 627], [cy1, cy1 + 21], color="#aaa", lw=0.8)
    ax.text(631, cy1 + 10, "CMOS 0.12µm - 6 Metal (1.20V)", fontsize=8, va="center")
    fig.savefig(out, dpi=100, facecolor="white"); plt.close(fig)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
