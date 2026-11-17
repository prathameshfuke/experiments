"""Render Microwind .MSK layouts (REC/TITLE records) like the Microwind 3.1 layout window.
Usage: python3 layout_render.py <msk> <out.png>
Layer colours and overlap colours were measured from a real Microwind 3.1 screenshot (black canvas, per-pixel composition).
Geometry comes from the file; the window chrome only imitates Microwind."""
import re, sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

PX_W, PX_H = 1600, 890
CV = dict(pdiff=(107, 81, 23), ndiff=(55, 126, 34), poly=(234, 51, 35), poly_diff=(239, 135, 51), metal=(0, 0, 246),
          metal_n=(55, 126, 247), metal_p=(107, 81, 246), poly_metal=(234, 51, 246),
          nw_edge=(42, 90, 26), nw_fill=(8, 18, 8), nw_dot=(26, 52, 26), dot=(78, 78, 46))


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
    cy0, cy1 = 76, 833
    CW, CH = PX_W, cy1 - cy0
    xs = [r[0] for r in recs] + [r[0] + r[2] for r in recs] + [t[0] for t in titles]
    ys = [r[1] for r in recs] + [r[1] + r[3] for r in recs] + [t[1] for t in titles]
    lx0, lx1, ly0, ly1 = min(xs) - 4, max(xs) + 8, min(ys) - 4, max(ys) + 6
    s = min((CW - 160) / (lx1 - lx0), (CH - 110) / (ly1 - ly0), 12.0)
    ox = (CW - s * (lx1 - lx0)) / 2 - lx0 * s
    oy = (CH - s * (ly1 - ly0)) / 2 + ly1 * s
    img = np.zeros((CH, CW, 3), np.uint8)
    for gx in (ox + k * 5 * s for k in range(-120, 400)):
        for gy in (oy - k * 5 * s for k in range(-120, 400)):
            if 0 <= gx < CW and 0 <= gy < CH: img[int(gy), int(gx)] = CV["dot"]
    mk = {l: np.zeros((CH, CW), bool) for l in ("NW", "DP", "DN", "PO", "ME")}
    for (x, y, w, h, l) in recs:
        if l in mk:
            xa, xb = int(round(ox + x * s)), int(round(ox + (x + w) * s)); ya, yb = int(round(oy - (y + h) * s)), int(round(oy - y * s))
            mk[l][max(ya, 0):max(yb, 0), max(xa, 0):max(xb, 0)] = True
    nw = mk["NW"]; img[nw] = CV["nw_fill"]
    yy, xx = np.nonzero(nw); sel = (xx % 4 == 0) & (yy % 4 == 0); img[yy[sel], xx[sel]] = CV["nw_dot"]
    dp, dn, po, me = mk["DP"], mk["DN"], mk["PO"], mk["ME"]
    img[dp] = CV["pdiff"]; img[dn] = CV["ndiff"]
    img[po & ~(dp | dn)] = CV["poly"]; img[po & (dp | dn)] = CV["poly_diff"]
    img[me & ~po & ~dp & ~dn] = CV["metal"]; img[me & dn & ~po] = CV["metal_n"]; img[me & dp & ~po] = CV["metal_p"]; img[me & po] = CV["poly_metal"]

    fig = plt.figure(figsize=(PX_W / 100, PX_H / 100), dpi=100, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PX_W); ax.set_ylim(PX_H, 0); ax.axis("off")
    R = lambda x, y, w, h, **k: ax.add_patch(Rectangle((x, y), w, h, **k))
    ax.imshow(img, extent=(0, CW, cy1, cy0), interpolation="nearest", aspect="auto", zorder=1)
    for (x, y, w, h, l) in recs:
        px, py = ox + x * s, cy0 + oy - (y + h) * s
        if l == "NW": R(px, py, w * s, h * s, fc="none", ec=tuple(v / 255 for v in CV["nw_edge"]), lw=1.2, zorder=2)
        if l == "CO":
            R(px, py, w * s, h * s, fc="none", ec="white", lw=1.0, zorder=3)
            ax.plot([px, px + w * s], [py, py + h * s], color="white", lw=0.9, zorder=3); ax.plot([px, px + w * s], [py + h * s, py], color="white", lw=0.9, zorder=3)
    for (x, y, t) in titles:
        ax.text(ox + x * s, cy0 + oy - y * s, t, color="white", fontsize=9, style="italic", va="bottom", zorder=4)
    ax.text(10, 92, "5 lambda", color="white", fontsize=7.5, va="center", zorder=4)
    ax.plot([6, 6 + 5 * s], [106, 106], color="white", lw=1.5, zorder=4); ax.text(10, 118, "%.3fµm" % (5 * 0.06), color="white", fontsize=7.5, va="center", zorder=4)
    # window chrome
    R(0, 0, PX_W, 24, fc="#f3f3f3", zorder=5); R(2, 4, 14, 14, fc="#222", zorder=6)
    ax.text(24, 12, "Microwind Version 3.1 - D:\\%s.MSK" % name, fontsize=9, va="center", color="#333", zorder=6)
    ax.text(1475, 12, "—", fontsize=10, va="center", color="#555", zorder=6); ax.text(1520, 12, "▢", fontsize=10, va="center", color="#555", zorder=6)
    ax.text(1568, 12, "✕", fontsize=10, va="center", color="#555", zorder=6)
    R(0, 24, PX_W, 21, fc="white", zorder=5)
    for lab, x in (("File", 7), ("View", 41), ("Edit", 81), ("Simulate", 117), ("Compile", 179), ("Analysis", 241), ("Help", 300)):
        ax.text(x, 34, lab, fontsize=8.5, va="center", color="#333", zorder=6)
    R(0, 45, PX_W, 31, fc="#c8c8c8", zorder=5)
    icol = ["#e8b300", "#2d6bd0", "#2db02d", "#222", "#2db02d", "#e8b300", "#555", "#555", "#d4a000", "#d33", "#2db02d", "#222",
            "#2d6bd0", "#2db02d", "#2d6bd0", "#222", "#d4a000", "#d33", "#2db02d", "#2d6bd0"]
    for i, c in enumerate(icol): R(8 + i * 27 + (12 if i > 7 else 0) + (14 if i > 13 else 0), 54, 14, 14, fc=c, zorder=6)
    R(0, cy1, PX_W, PX_H - cy1, fc="#f0f0f0", zorder=5)
    ax.text(3, cy1 + 10, 'Saved %d boxes in "D:\\%s.MSK"' % (len(recs), name), fontsize=8, va="center", zorder=6); ax.plot([470, 470], [cy1, cy1 + 21], color="#aaa", lw=0.8, zorder=6)
    ax.text(474, cy1 + 10, "Hit %d" % (len(recs) + 1), fontsize=8, va="center", zorder=6); ax.plot([627, 627], [cy1, cy1 + 21], color="#aaa", lw=0.8, zorder=6)
    ax.text(631, cy1 + 10, "CMOS 0.12µm - 6 Metal (1.20V)", fontsize=8, va="center", zorder=6)
    fig.savefig(out, dpi=100, facecolor="white"); plt.close(fig)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
