"""Block diagrams (Exp 1-5) and gate / transistor schematics (Exp 6-8)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
import schemdraw.logic as logic

I = "../img/"

def block(out, name, ins, outs, w=3.0):
    h = max(len(ins), len(outs)) * 0.7 + 0.8
    fig, ax = plt.subplots(figsize=(6, h * 0.9 + 0.4))
    ax.add_patch(plt.Rectangle((0, 0), w, h, fill=False, lw=2))
    ax.text(w / 2, h / 2, name, ha="center", va="center", fontsize=13, weight="bold")
    for k, s in enumerate(ins):
        y = h - 0.6 - k * 0.7
        ax.plot([-0.9, 0], [y, y], "k", lw=1.5); ax.text(-0.95, y, s, ha="right", va="center", fontsize=10)
    for k, s in enumerate(outs):
        y = h - 0.6 - k * 0.7
        ax.plot([w, w + 0.9], [y, y], "k", lw=1.5); ax.text(w + 0.95, y, s, ha="left", va="center", fontsize=10)
    ax.set_xlim(-3.2, w + 3.2); ax.set_ylim(-0.2, h + 0.2); ax.axis("off")
    fig.savefig(out, dpi=150, bbox_inches="tight"); plt.close(fig)

block(I + "exp1_block.png", "4-bit ALU", ["A[3:0]", "B[3:0]", "S[2:0]"], ["Y[3:0]"])
block(I + "exp2_block.png", "Universal Shift Register", ["clk", "S[1:0]", "IL", "IR", "P[3:0]"], ["Q[3:0]"], w=4.0)
block(I + "exp3_block.png", "4-bit Up/Down Counter", ["clk", "rst", "en", "up"], ["Qout[3:0]"], w=4.0)
block(I + "exp4_block.png", "FIFO 8 x 8", ["clk", "reset", "w", "r", "d[7:0]"], ["q[7:0]", "empty", "full"])
block(I + "exp5_block.png", "4x4 Keypad Scanner", ["clk", "col[3:0]"], ["row[3:0]", "led[15:0]", "hex[3:0]"], w=3.6)

def save(d, name):
    d.save(I + name, dpi=150)

def gate_fig(name, build):
    d = schemdraw.Drawing(show=False); d.config(fontsize=11, unit=2.5)
    build(d); save(d, name)

def b_inv(d):
    g = d.add(logic.Not().label("Y = A'", "right")); d.add(logic.Line().at(g.in1).left(1).label("A", "left"))
def b_nand(d):
    g = d.add(logic.Nand().label("Y", "right")); d.add(logic.Line().at(g.in1).left(1).label("A", "left")); d.add(logic.Line().at(g.in2).left(1).label("B", "left"))
def b_nor(d):
    g = d.add(logic.Nor().label("Y", "right")); d.add(logic.Line().at(g.in1).left(1).label("A", "left")); d.add(logic.Line().at(g.in2).left(1).label("B", "left"))
def wire(d, *pts):
    for p, q in zip(pts, pts[1:]):
        d.add(logic.Line().at(p).to(q))
def dot(d, p): d.add(logic.Dot().at(p))
def label(d, p, txt): d.add(elm.Label().at(p).label(txt, "left"))

def b_ha(d):
    x = d.add(logic.Xor().at((4, 2)).label("Sum = A xor B", "right"))
    a = d.add(logic.And().at((4, 0)).label("Carry = A.B", "right"))
    xa, xb, aa, ab = x.in1, x.in2, a.in1, a.in2
    ax, bx = 1.0, 2.0
    wire(d, (0, xa[1]), xa); wire(d, (ax, xa[1]), (ax, aa[1]), aa)
    wire(d, (0, ab[1]), ab); wire(d, (bx, xb[1]), (bx, ab[1])); wire(d, (bx, xb[1]), xb)
    dot(d, (ax, xa[1])); dot(d, (bx, ab[1]))
    label(d, (0, xa[1]), "A"); label(d, (0, ab[1]), "B")

def b_mux(d):
    n = d.add(logic.Not().at((2, 1.6)))
    t = d.add(logic.And().at((5, 3)))
    b = d.add(logic.And().at((5, 0)))
    o = d.add(logic.Or().at((8, 1.5)).label("Y = S.D1 + S'.D0", "right"))
    wire(d, t.out, (7, t.out[1]), o.in1); wire(d, b.out, (7, b.out[1]), o.in2)
    wire(d, (0, t.in1[1]), t.in1); label(d, (0, t.in1[1]), "D1")
    wire(d, (0, b.in2[1]), b.in2); label(d, (0, b.in2[1]), "D0")
    sy = n.in1[1]
    wire(d, (0, sy), n.in1); label(d, (0, sy), "S")
    wire(d, (1, sy), (1, t.in2[1]), t.in2); dot(d, (1, sy))
    wire(d, n.out, (4, n.out[1]), (4, b.in1[1]), b.in1)

gate_fig("exp6_inverter_sch.png", b_inv)
gate_fig("exp6_nand_sch.png", b_nand)
gate_fig("exp6_nor_sch.png", b_nor)
gate_fig("exp6_halfadder_sch.png", b_ha)
gate_fig("exp7_mux_gates_sch.png", b_mux)
