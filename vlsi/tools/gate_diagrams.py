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
    for y, a, g1, g2 in ((1.2, "A", "S", "S'"), (-1.2, "B", "S'", "S")):
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
VDDY, PY, BUS, NY, GNDY = 9.5, 7.0, 4.3, 1.6, -1.6


class Stick:
    def __init__(self, title, width, note=None):
        self.fig, self.ax = plt.subplots(figsize=(max(3.6, (width + 4) * 0.5), 4.7), dpi=170)
        ax = self.ax; ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(title + " - stick diagram", fontsize=11, weight="bold", color=INK)
        ax.set_xlim(-2.2, width + 2.2); ax.set_ylim(-2.6, 10.6)
        self.w = width
        if note: ax.text(width / 2, -2.4, note, ha="center", fontsize=7, style="italic", color="#374151")

    def rails(self, x1, x2, xv=None):
        ax = self.ax
        ax.plot([x1, x2], [VDDY, VDDY], color=METAL, lw=4); ax.text(x1 - 0.2, VDDY, "VDD", ha="right", va="center", color=METAL, fontsize=9, weight="bold")
        ax.plot([x1, x2], [GNDY, GNDY], color=METAL, lw=4); ax.text(x1 - 0.2, GNDY, "GND", ha="right", va="center", color=METAL, fontsize=9, weight="bold")

    def diff(self, row, x1, x2):
        y, c = (PY, ORANGE) if row == "p" else (NY, GREEN)
        self.ax.plot([x1, x2], [y, y], color=c, lw=6, solid_capstyle="butt")

    def poly(self, x, label, full=True, row=None):
        if full: y1, y2, ly, va = -0.6, 8.4, 8.8, "bottom"
        elif row == "p": y1, y2, ly, va = 5.8, 8.4, 8.8, "bottom"
        else: y1, y2, ly, va = -0.6, 2.8, -0.8, "top"
        self.ax.plot([x, x], [y1, y2], color=POLY, lw=3, solid_capstyle="butt")
        self.ax.text(x, ly, label, ha="center", va=va, color=POLY, fontsize=10, weight="bold")

    def con(self, x, y):
        self.ax.add_patch(Rectangle((x - 0.17, y - 0.17), 0.34, 0.34, fc="black", zorder=4))

    def wire(self, *pts):
        self.ax.plot([p[0] for p in pts], [p[1] for p in pts], color=METAL, lw=3, solid_capstyle="round", solid_joinstyle="round")

    def label(self, x, y, t, **k):
        self.ax.text(x, y, t, fontsize=10, weight="bold", va="center", **k)

    # node helpers: contact on diffusion + metal to a target
    def to_vdd(self, x): self.con(x, PY); self.wire((x, PY), (x, VDDY))
    def to_gnd(self, x): self.con(x, NY); self.wire((x, NY), (x, GNDY))
    def p_out(self, x): self.con(x, PY); self.wire((x, PY), (x, BUS))
    def n_out(self, x): self.con(x, NY); self.wire((x, NY), (x, BUS))


def gate_block(s, x0, kind, ins):
    """NOT / NAND / NOR block with nodes at x0+1, +3, (+5); returns the x of its output bus node."""
    n = len(ins); xe = x0 + 2 * n + 1
    s.diff("p", x0 + 1, xe); s.diff("n", x0 + 1, xe)
    for i, nm in enumerate(ins): s.poly(x0 + 2 + 2 * i, nm)
    if kind == "not":
        s.to_vdd(x0 + 1); s.to_gnd(x0 + 1); s.p_out(x0 + 3); s.n_out(x0 + 3); return x0 + 3
    if kind == "nand":  # p parallel (VDD at ends, Y middle); n series (GND left, Y right)
        s.to_vdd(x0 + 1); s.to_vdd(x0 + 5); s.p_out(x0 + 3); s.to_gnd(x0 + 1); s.n_out(x0 + 5)
        s.wire((x0 + 3, BUS), (x0 + 5, BUS)); return x0 + 5
    # nor: p series (VDD left, Y right); n parallel (GND at ends, Y middle)
    s.to_vdd(x0 + 1); s.p_out(x0 + 5); s.to_gnd(x0 + 1); s.to_gnd(x0 + 5); s.n_out(x0 + 3)
    s.wire((x0 + 3, BUS), (x0 + 5, BUS)); return x0 + 5


def stick(kind):
    if kind in ("not", "nand", "nor"):
        ins = ["A"] if kind == "not" else ["A", "B"]; w = 4 if kind == "not" else 6
        s = Stick({"not": "NOT", "nand": "NAND", "nor": "NOR"}[kind], w + 2)
        s.rails(0, w + 1); xo = gate_block(s, 0, kind, ins)
        s.wire((xo, BUS), (xo + 1.6, BUS)); s.label(xo + 1.8, BUS, "Y"); return s.fig
    if kind in ("and", "or"):
        first = "nand" if kind == "and" else "nor"
        s = Stick(kind.upper() + " = %s + inverter" % first.upper(), 14)
        s.rails(0, 13); xo = gate_block(s, 0, first, ["A", "B"])
        xi = 9; xo2 = gate_block(s, 7, "not", ["X"])
        s.wire((xo, BUS), (xi, BUS)); s.con(xi, BUS)
        s.wire((xo2, BUS), (xo2 + 1.6, BUS)); s.label(xo2 + 1.8, BUS, "Y"); return s.fig
    if kind in ("xor", "xnor"):
        s = Stick(kind.upper(), 12, "poly stubs with the same name are joined by metal; A' and B' come from two inverters")
        s.rails(0, 12)
        p1, p2 = (("A", "B'"), ("A'", "B")) if kind == "xor" else (("A", "B"), ("A'", "B'"))
        n1, n2 = (("A", "B"), ("A'", "B'")) if kind == "xor" else (("A", "B'"), ("A'", "B"))
        for (x, g) in ((2, p1[0]), (4, p1[1]), (8, p2[0]), (10, p2[1])): s.poly(x, g, False, "p")
        for (x, g) in ((2, n1[0]), (4, n1[1]), (8, n2[0]), (10, n2[1])): s.poly(x, g, False, "n")
        s.diff("p", 1, 5); s.diff("p", 7, 11); s.diff("n", 1, 5); s.diff("n", 7, 11)
        s.to_vdd(1); s.to_vdd(11); s.p_out(5); s.p_out(7); s.n_out(1); s.n_out(11)
        s.to_gnd(5); s.to_gnd(7)
        s.wire((1, BUS), (11, BUS)); s.wire((11, BUS), (12.6, BUS)); s.label(12.8, BUS, "Y"); return s.fig
    if kind == "tg":
        s = Stick("Transmission gate", 4, "S and S' poly are separate; IN joins both left nodes, OUT both right nodes")
        s.diff("p", 1, 3); s.diff("n", 1, 3); s.poly(2, "S'", False, "p"); s.poly(2, "S", False, "n")
        for x in (1, 3): s.con(x, PY); s.con(x, NY); s.wire((x, NY), (x, PY))
        s.wire((-0.6, BUS), (1, BUS)); s.label(-0.8, BUS, "IN", ha="right"); s.wire((3, BUS), (4.6, BUS)); s.label(4.8, BUS, "OUT")
        return s.fig
    if kind == "mux":
        s = Stick("2:1 MUX (two transmission gates)", 10, "S' is made by one inverter on S (not drawn)")
        for x0, flip, ins, ng, pg in ((0, False, "A", "S'", "S"), (6, True, "B", "S", "S'")):
            s.diff("p", x0 + 1, x0 + 3); s.diff("n", x0 + 1, x0 + 3)
            s.poly(x0 + 2, pg, False, "p"); s.poly(x0 + 2, ng, False, "n")
            for x in (x0 + 1, x0 + 3): s.con(x, PY); s.con(x, NY); s.wire((x, NY), (x, PY))
        s.wire((-0.6, BUS), (1, BUS)); s.label(-0.8, BUS, "A", ha="right")
        s.wire((9, BUS), (10.6, BUS)); s.label(10.8, BUS, "B")
        s.wire((3, BUS), (7, BUS)); s.wire((5, BUS), (5, 5.8)); s.label(5, 6.3, "Y", ha="center")
        return s.fig
    if kind == "sram":
        s = Stick("6T SRAM cell", 12, "WL, Q and Q' poly of the same name are joined by metal")
        s.rails(2.2, 9.8)
        s.diff("p", 3, 5); s.diff("p", 7, 9); s.diff("n", 1, 5); s.diff("n", 7, 11)
        s.poly(4, "Q'"); s.poly(8, "Q")
        s.poly(2, "WL", False, "n"); s.poly(10, "WL", False, "n")
        s.to_vdd(3); s.to_vdd(9); s.to_gnd(5); s.to_gnd(7)
        s.p_out(5); s.n_out(3); s.wire((3, BUS), (5, BUS)); s.label(3.75, BUS + 0.7, "Q", ha="right")
        s.p_out(7); s.n_out(9); s.wire((7, BUS), (9, BUS)); s.label(8.25, BUS + 0.7, "Q'", ha="left")
        for x, t in ((1, "BL"), (11, "BL'")):
            s.con(x, NY); s.wire((x, NY), (x, -0.3)); s.label(x, -0.85, t, ha="center")
        return s.fig


GATES = [("NOT (Inverter)", "not", b_not, (3.6, 4.6)), ("NAND (4T)", "nand", b_nand, (4.6, 4.6)),
         ("NOR (4T)", "nor", b_nor, (4.6, 4.6)), ("AND = NAND + inverter (6T)", "and", b_and, (8.4, 5.0)),
         ("OR = NOR + inverter (6T)", "or", b_or, (8.4, 5.0)), ("XOR (8T + inverters for A', B')", "xor", b_xor, (4.6, 4.8)),
         ("XNOR (8T + inverters for A', B')", "xnor", b_xnor, (4.6, 4.8)), ("Transmission gate (2T)", "tg", b_tg, (5.4, 3.2)),
         ("2:1 MUX with transmission gates", "mux", b_mux, (6.2, 4.0)), ("6T SRAM cell", "sram", b_sram, (9.0, 5.6))]

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for title, key, fn, sz in GATES:
        f = fig_for(title, fn, sz); f.savefig(os.path.join(out, "gate_%s.png" % key), facecolor="white"); plt.close(f)
    for kind in ("not", "nand", "nor", "and", "or", "xor", "xnor", "tg", "mux", "sram"):
        f = stick(kind); f.savefig(os.path.join(out, "stick_%s.png" % kind), facecolor="white"); plt.close(f)
    print("done")
