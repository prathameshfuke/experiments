"""Transistor-level CMOS gate diagrams and colour stick diagrams.
Usage: python3 gate_diagrams.py <outdir>"""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

INK, RED = "#1f2a37", "#b3261e"
STEP = 1.5  # vertical pitch of one transistor


def mos(ax, x, y, gate, kind):
    """Vertical MOSFET centred at (x, y); drain/source wire on x+0.35."""
    xw = x + 0.35
    ax.plot([x, x], [y - 0.4, y + 0.4], color=INK, lw=2)
    ax.plot([x - 0.14, x - 0.14], [y - 0.32, y + 0.32], color=INK, lw=2)
    gx = x - 0.14
    if kind == "p":
        ax.add_patch(Circle((gx - 0.07, y), 0.07, fc="white", ec=INK, lw=1.3, zorder=3)); gx -= 0.14
    ax.plot([gx, gx - 0.45], [y, y], color=INK, lw=2)
    ax.text(gx - 0.5, y, gate, ha="right", va="center", fontsize=11, weight="bold", color=INK)
    for dy in (-0.4, 0.4):
        ax.plot([x, xw], [y + dy, y + dy], color=INK, lw=2)
    ax.text(xw + 0.1, y + 0.45, kind.upper(), fontsize=7, color="#6b7280")
    return xw


def stack(ax, xc, ytop, gates, kind):
    """Series chain below ytop. Returns (x_wire, top, bottom) of the chain's wire."""
    ys = [ytop - 0.6 - i * STEP for i in range(len(gates))]
    for g, y in zip(gates, ys):
        xw = mos(ax, xc, y, g, kind)
    ax.plot([xw, xw], [ys[0] + 0.4, ys[-1] - 0.4], color=INK, lw=2)
    return xw, ys[0] + 0.4, ys[-1] - 0.4


def cmos(ax, ox, oy, pu, pd, out, outx=None):
    """pu/pd: parallel branches, each a list of series gate names. oy = VDD level.
    Returns (ymid, ygnd, xo)."""
    dx = 2.4
    hp = max(len(b) for b in pu) * STEP
    hn = max(len(b) for b in pd) * STEP
    ymid = oy - 0.3 - hp - 0.4
    ygnd = ymid - 0.3 - hn - 0.2
    xs_p, xs_n = [], []
    for i, b in enumerate(pu):
        xw, top, bot = stack(ax, ox + i * dx, oy - 0.3, b, "p"); xs_p.append(xw)
        ax.plot([xw, xw], [top, oy], color=INK, lw=2); ax.plot([xw, xw], [bot, ymid], color=INK, lw=2)
    for i, b in enumerate(pd):
        xw, top, bot = stack(ax, ox + i * dx, ymid - 0.3, b, "n"); xs_n.append(xw)
        ax.plot([xw, xw], [top, ymid], color=INK, lw=2); ax.plot([xw, xw], [bot, ygnd], color=INK, lw=2)
    xc = (xs_p[0] + xs_p[-1]) / 2
    ax.plot([xs_p[0], xs_p[-1]], [oy, oy], color=INK, lw=2)
    ax.plot([xc - 0.4, xc + 0.4], [oy + 0.1, oy + 0.1], color=RED, lw=4); ax.plot([xc, xc], [oy, oy + 0.1], color=INK, lw=2)
    ax.text(xc, oy + 0.25, "VDD", color=RED, ha="center", fontsize=10, weight="bold")
    ax.plot([xs_p[0], xs_p[-1]], [ymid, ymid], color=INK, lw=2)
    ax.plot([xs_n[0], xs_n[-1]], [ymid, ymid], color=INK, lw=2)
    ax.plot([xs_n[0], xs_n[-1]], [ygnd, ygnd], color=INK, lw=2)
    xg = (xs_n[0] + xs_n[-1]) / 2
    for k, w in enumerate((0.35, 0.22, 0.1)):
        ax.plot([xg - w, xg + w], [ygnd - 0.12 - k * 0.1] * 2, color=INK, lw=2)
    ax.plot([xg, xg], [ygnd, ygnd - 0.12], color=INK, lw=2)
    xr = max(xs_p + xs_n)
    xo = outx if outx is not None else xr + 0.8
    ax.plot([xr, xo], [ymid, ymid], color=INK, lw=2)
    ax.plot(xr, ymid, "o", color=INK, ms=5)
    ax.text(xo + 0.1, ymid, out, va="center", fontsize=11, weight="bold", color=INK)
    return ymid, ygnd, xo


def fig_for(name, build, size):
    fig, ax = plt.subplots(figsize=size, dpi=170)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(name, fontsize=12, weight="bold", color=INK)
    build(ax)
    ax.autoscale_view(); ax.margins(0.06)
    return fig


def b_not(ax): cmos(ax, 0, 0, [["A"]], [["A"]], "Y = A'")
def b_nand(ax): cmos(ax, 0, 0, [["A"], ["B"]], [["A", "B"]], "Y = (AB)'")
def b_nor(ax): cmos(ax, 0, 0, [["A", "B"]], [["A"], ["B"]], "Y = (A+B)'")


def b_and(ax):
    ym, yg, xo = cmos(ax, 0, 0, [["A"], ["B"]], [["A", "B"]], "", outx=4.2)
    ax.text(3.2, ym + 0.2, "X = (AB)'", ha="center", fontsize=10, style="italic")
    cmos(ax, 5.0, 0, [["X"]], [["X"]], "Y = AB")


def b_or(ax):
    ym, yg, xo = cmos(ax, 0, 0, [["A", "B"]], [["A"], ["B"]], "", outx=4.2)
    ax.text(3.2, ym + 0.2, "X = (A+B)'", ha="center", fontsize=10, style="italic")
    cmos(ax, 5.0, 0, [["X"]], [["X"]], "Y = A+B")


def b_xor(ax):  # Y = A'B + AB'; complementary inputs A', B' come from two inverters
    cmos(ax, 0, 0, [["A", "B'"], ["A'", "B"]], [["A", "B"], ["A'", "B'"]], "Y = A xor B")


def b_xnor(ax):
    cmos(ax, 0, 0, [["A", "B"], ["A'", "B'"]], [["A", "B'"], ["A'", "B"]], "Y = A xnor B")


def b_tg(ax):  # transmission gate: NMOS and PMOS in parallel
    for y, kind, g in ((0.8, "n", "S"), (-0.8, "p", "S'")):
        xc = 2.3
        ax.plot([xc, xc], [y - 0.4, y + 0.4], color=INK, lw=2)
        ax.plot([xc - 0.14] * 2, [y - 0.32, y + 0.32], color=INK, lw=2)
        gx = xc - 0.14
        if kind == "p":
            ax.add_patch(Circle((gx - 0.07, y), 0.07, fc="white", ec=INK, lw=1.3, zorder=3)); gx -= 0.14
        ax.plot([gx, gx - 0.6], [y, y], color=INK, lw=2)
        ax.text(gx - 0.65, y, g, ha="right", va="center", fontsize=11, weight="bold")
        for dy in (-0.4, 0.4):
            ax.plot([1.2, 3.4], [y + dy, y + dy], color=INK, lw=2)
    ax.plot([1.2, 1.2], [-1.2, 1.2], color=INK, lw=2); ax.plot([3.4, 3.4], [-1.2, 1.2], color=INK, lw=2)
    ax.plot([0, 1.2], [0, 0], color=INK, lw=2); ax.plot([3.4, 4.6], [0, 0], color=INK, lw=2)
    ax.plot([1.2, 3.4], [0.4, 0.4], color=INK, lw=0)
    ax.text(0, 0.2, "IN", ha="center", fontsize=11, weight="bold"); ax.text(4.6, 0.2, "OUT", ha="center", fontsize=11, weight="bold")
    ax.set_ylim(-2, 2)


def b_mux(ax):  # 2:1 mux from two transmission gates
    for y, a, g1, g2 in ((1.2, "A", "S'", "S"), (-1.2, "B", "S", "S'")):
        ax.text(-0.3, y, a, ha="right", va="center", fontsize=11, weight="bold")
        ax.plot([0, 1], [y, y], color=INK, lw=2)
        ax.add_patch(Rectangle((1, y - 0.55), 2, 1.1, fc="#eef2ff", ec=INK, lw=1.6))
        ax.text(2, y, "TG", ha="center", va="center", fontsize=11, weight="bold")
        ax.text(2, y + 0.75, "n:" + g2 + "  p:" + g1, ha="center", fontsize=8, color="#374151")
        ax.plot([3, 4.4], [y, y], color=INK, lw=2)
    ax.plot([4.4, 4.4], [-1.2, 1.2], color=INK, lw=2); ax.plot([4.4, 5.4], [0, 0], color=INK, lw=2); ax.plot(4.4, 0, "o", color=INK, ms=5)
    ax.text(5.5, 0, "Y = S'A + SB", va="center", fontsize=11, weight="bold")
    ax.text(2, -2.6, "S' made by one inverter on S", ha="center", fontsize=8.5, style="italic", color="#374151")
    ax.set_ylim(-3, 2.4)


def b_sram(ax):  # cross-coupled inverters (4T) + two access NMOS (2T)
    ym, yg, _ = cmos(ax, 0, 0, [["Q'"]], [["Q'"]], "", outx=2.2)
    cmos(ax, 4.2, 0, [["Q"]], [["Q"]], "", outx=6.4)
    ax.text(1.5, ym + 0.2, "Q", fontsize=11, weight="bold"); ax.text(5.7, ym + 0.2, "Q'", fontsize=11, weight="bold")
    for xt, xl, bl in ((-2.6, 0.35, "BL"), (8.2, 6.4, "BL'")):
        xw = mos(ax, xt, -1.4, "WL", "n")
        ax.plot([xw, xw], [-1.0, -0.5], color=INK, lw=2); ax.text(xw, -0.35, bl, ha="center", fontsize=10, weight="bold")
        ax.plot([xw, xw], [-1.8, ym], color=INK, lw=2); ax.plot([xw, xl], [ym, ym], color=INK, lw=2)
    ax.text(3.0, -5.6, "2 PMOS + 4 NMOS (cross-coupled inverters) + 2 NMOS access = 6T", ha="center", fontsize=8.5, weight="bold")


GREEN, ORANGE, POLY, METAL = "#2eaa3c", "#e8a317", "#d62828", "#2f5be7"


def stick(name, inputs, kind):
    """Stick diagram: green n-diff, orange p-diff, red poly, blue metal, black contacts."""
    fig, ax = plt.subplots(figsize=(4.6, 4.6), dpi=170)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(name + " - stick diagram", fontsize=11, weight="bold", color=INK)
    n = len(inputs); W = 2 + 2 * n
    ax.plot([0, W], [8, 8], color=METAL, lw=4); ax.text(-0.2, 8, "VDD", ha="right", va="center", color=METAL, fontsize=9, weight="bold")
    ax.plot([0, W], [0, 0], color=METAL, lw=4); ax.text(-0.2, 0, "GND", ha="right", va="center", color=METAL, fontsize=9, weight="bold")
    ax.plot([1, W - 1], [6, 6], color=ORANGE, lw=5, solid_capstyle="butt"); ax.text(W - 0.9, 6.5, "p-diff", fontsize=7, color=ORANGE)
    ax.plot([1, W - 1], [2, 2], color=GREEN, lw=5, solid_capstyle="butt"); ax.text(W - 0.9, 1.3, "n-diff", fontsize=7, color=GREEN)
    cols = [2 + 2 * i for i in range(n)]
    for c, nm in zip(cols, inputs):
        ax.plot([c, c], [-0.8, 7], color=POLY, lw=3); ax.text(c, -1.3, nm, ha="center", color=POLY, fontsize=10, weight="bold")

    def con(x, y): ax.add_patch(Rectangle((x - 0.15, y - 0.15), 0.3, 0.3, fc="black", zorder=4))

    def wire(x1, y1, x2, y2): ax.plot([x1, x2], [y1, y2], color=METAL, lw=3)
    out = lambda x: (wire(x, 4, W + 0.6, 4), ax.text(W + 0.7, 4, "Y", va="center", fontsize=10, weight="bold"))
    if kind == "not":
        con(1, 6); wire(1, 6, 1, 8); con(1, 2); wire(1, 2, 1, 0)
        con(3, 6); con(3, 2); wire(3, 2, 3, 6); out(3)
    elif kind == "nand":  # p in parallel to VDD, n in series to GND
        for x in (1, 5): con(x, 6); wire(x, 6, x, 8)
        con(3, 6); con(3, 2); wire(3, 2, 3, 6); out(3)
        con(1, 2); wire(1, 2, 1, 0)
    else:  # nor: p in series from VDD, n in parallel to GND
        con(1, 6); wire(1, 6, 1, 8)
        con(5, 6); con(5, 2); wire(5, 2, 5, 6); out(5)
        for x in (1, 3): con(x, 2); wire(x, 2, x, 0)
    ax.set_xlim(-1.8, W + 1.6); ax.set_ylim(-2, 9)
    return fig


GATES = [("NOT (Inverter)", "not", b_not, (3.6, 4.6)), ("NAND (4T)", "nand", b_nand, (4.6, 4.6)),
         ("NOR (4T)", "nor", b_nor, (4.6, 4.6)), ("AND = NAND + inverter (6T)", "and", b_and, (8.4, 5.0)),
         ("OR = NOR + inverter (6T)", "or", b_or, (8.4, 5.0)), ("XOR (8T + inverters for A', B')", "xor", b_xor, (4.6, 4.8)),
         ("XNOR (8T + inverters for A', B')", "xnor", b_xnor, (4.6, 4.8)), ("Transmission gate (2T)", "tg", b_tg, (5.4, 3.2)),
         ("2:1 MUX with transmission gates", "mux", b_mux, (6.2, 4.0)), ("6T SRAM cell", "sram", b_sram, (9.0, 5.6))]

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for title, key, fn, sz in GATES:
        f = fig_for(title, fn, sz); f.savefig(os.path.join(out, "gate_%s.png" % key), facecolor="white"); plt.close(f)
    for title, kind, ins in (("NOT", "not", ["A"]), ("NAND", "nand", ["A", "B"]), ("NOR", "nor", ["A", "B"])):
        f = stick(title, ins, kind); f.savefig(os.path.join(out, "stick_%s.png" % kind), facecolor="white"); plt.close(f)
    print("done")
