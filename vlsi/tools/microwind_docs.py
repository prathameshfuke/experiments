"""Microwind-style analog-simulation images (with / without load capacitance) and the EXP 06/07/08 documents.
Run from vlsi/:  python3 tools/microwind_docs.py
 - renders wave_<circuit>_<nocap|cap>.png into each experiment's img/ folder (landscape, 1600x900)
 - EXP 06: writes one docx per gate (NOT, NAND, NOR, Half adder); EXP 07/08: swaps in the new waveform images
Then run:  python3 tools/build_pdfs.py <docx...>"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from docx import Document
from docx.shared import Cm, Pt
from cmos import *
from layout_render import render as render_layout

# ------------------------------------------------------------------ circuits
def inv(c, a, y): c.p(y, a, "vdd"); c.n(y, a, "gnd")
def nand(c, a, b, y, tag): m = tag + "_m"; c.p(y, a, "vdd"); c.p(y, b, "vdd"); c.n(y, a, m, 2); c.n(m, b, "gnd", 2)
def nor(c, a, b, y, tag): m = tag + "_m"; c.p(m, a, "vdd", 4); c.p(y, b, m, 4); c.n(y, a, "gnd"); c.n(y, b, "gnd")
def rails(c): c.drive("vdd", lambda t: VDD); c.drive("gnd", lambda t: 0.0)
def load(c, node, cl): c.node(node, CPAR + cl)


def run_inv(cl):
    c = Circuit(); rails(c); load(c, "y", cl); inv(c, "a", "y")
    c.drive("a", pulse_seq([0, 1, 0, 1, 0, 1], 1e-9, t0=0.5e-9)); return c.run(6.5e-9)


def run_gate(kind, cl):
    c = Circuit(); rails(c); load(c, "y", cl); (nand if kind == "nand" else nor)(c, "a", "b", "y", "g")
    c.drive("a", pulse_seq([0, 0, 1, 1, 0], 1e-9)); c.drive("b", pulse_seq([0, 1, 0, 1, 0], 1e-9)); return c.run(5e-9)


def run_ha(cl):
    c = Circuit(); rails(c); load(c, "s", cl); load(c, "co", cl)
    nand(c, "a", "b", "n1", "h1"); nand(c, "a", "n1", "n2", "h2"); nand(c, "b", "n1", "n3", "h3"); nand(c, "n2", "n3", "s", "h4")
    nand(c, "a", "b", "n5", "h5"); inv(c, "n5", "co")
    c.drive("a", pulse_seq([0, 0, 1, 1], 2e-9)); c.drive("b", pulse_seq([0, 1, 0, 1], 2e-9)); return c.run(8e-9)


def run_mux(kind, cl):
    c = Circuit(); rails(c); load(c, "y", cl); inv(c, "s", "sb")
    if kind == "gates": nand(c, "d1", "s", "n1", "m1"); nand(c, "d0", "sb", "n2", "m2"); nand(c, "n1", "n2", "y", "m3")
    else: c.tg("d0", "y", "sb", "s"); c.tg("d1", "y", "s", "sb")
    seq = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
    for idx, name in enumerate(("s", "d1", "d0")): c.drive(name, pulse_seq([q[idx] for q in seq], 1.5e-9))
    return c.run(12e-9)


def run_sram(cl):
    c = Circuit(); rails(c); n = 1e-9
    c.node("q", v0=0.0); c.node("qb", v0=VDD)
    c.p("q", "qb", "vdd", 1.0); c.n("q", "qb", "gnd", 3.0); c.p("qb", "q", "vdd", 1.0); c.n("qb", "q", "gnd", 3.0)
    c.n("bl", "wl", "q", 2.0); c.n("blb", "wl", "qb", 2.0); c.node("bl", CPAR + cl); c.node("blb", CPAR + cl)
    c.drive("wl", pwl([(0, 0), (1*n, 0), (1.03*n, VDD), (3*n, VDD), (3.03*n, 0), (5*n, 0), (5.03*n, VDD), (6*n, VDD), (6.03*n, 0),
                       (6.5*n, 0), (6.53*n, VDD), (8*n, VDD), (8.03*n, 0)]))
    def bl(t):
        if 1e-9 <= t < 3e-9 or 4e-9 <= t < 5e-9: return VDD
        if 5e-9 <= t < 6e-9: return None
        if 6.5e-9 <= t < 8e-9: return 0.0
        return 0.0 if t < 1e-9 else None
    def blb(t):
        if 1e-9 <= t < 3e-9: return 0.0
        if 4e-9 <= t < 5e-9 or 6.5e-9 <= t < 8e-9: return VDD
        if 5e-9 <= t < 6e-9: return None
        return VDD if t < 1e-9 else None
    c.drive("bl", bl); c.drive("blb", blb); c.init["bl"] = 0.0; c.init["blb"] = VDD
    return c.run(8.5e-9)


# ------------------------------------------------------------------ Microwind-style window
GREEN, RED = "#19e019", "#ff2a1f"


def crossings(t, y, level=VDD / 2):
    i = np.where((y[:-1] - level) * (y[1:] - level) < 0)[0]
    return [t[k] + (level - y[k]) / (y[k + 1] - y[k]) * (t[k + 1] - t[k]) for k in i]


def window(tr, rows, outs, tend, fname, out, cap):
    """rows: [(node, label)], outs: output node names (red); everything else green."""
    W, H = 1600, 900
    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")
    R = lambda x, y, w, h, **k: ax.add_patch(Rectangle((x, y), w, h, **k))
    R(0, 0, W, 26, fc="white"); R(5, 6, 14, 14, fc="#222")
    ax.text(26, 13, "Analog simulation of D:\\CMOS_%s" % fname, fontsize=8.5, va="center", color="#333")
    ax.text(1508, 13, "—", fontsize=10, va="center"); ax.text(1535, 13, "▢", fontsize=10, va="center"); ax.text(1570, 13, "✕", fontsize=10, va="center")
    x0, x1, y0, y1, gap = 78, 1318, 36, 800, 12
    n = len(rows); h = (y1 - y0 - gap * (n - 1)) / n
    step = 1e-9 if tend <= 7e-9 else 2e-9
    px = lambda t: x0 + t / tend * (x1 - x0)
    outs_t = [(nm, crossings(tr["t"], tr[nm])) for nm in outs[:1]]
    ins_t = sorted(t for nm, _ in rows if nm not in outs for t in crossings(tr["t"], tr[nm]))
    for k, (nm, lab) in enumerate(rows):
        top = y0 + k * (h + gap); R(x0, top, x1 - x0, h, fc="black", ec="#777", lw=0.8)
        py = lambda v, top=top: top + h - 6 - (v / VDD) * (h - 14)
        for g in np.arange(0, tend + 1e-15, step):
            ax.plot([px(g)] * 2, [top, top + h], color="white", lw=0.7, ls=(0, (3, 3)), alpha=0.85)
        for v in (0.0, VDD):
            ax.plot([x0, x1], [py(v)] * 2, color="white", lw=0.5, ls=(0, (1, 3)), alpha=0.7)
        ax.plot(px(tr["t"]), py(np.clip(tr[nm], 0, VDD)), color=RED if nm in outs else GREEN, lw=1.6)
        ax.text(x0 - 6, py(VDD), "%.2f" % VDD, ha="right", va="center", fontsize=7.5)
        ax.text(x0 - 6, py(0), "0.0", ha="right", va="center", fontsize=7.5)
        ax.text(14, top + h / 2, lab, rotation=90, va="center", ha="center", fontsize=9)
    for nm, ts in outs_t:
        for to in ts:
            cand = [t for t in ins_t if 0 < to - t < 0.7e-9]
            if not cand: continue
            ti = max(cand)
            for tt in (ti, to): ax.plot([px(tt)] * 2, [y0, y1], color="white", lw=0.9, ls=(0, (1, 2)))
            ax.text(px((ti + to) / 2) + 14, y1 - 30, "%dps" % round((to - ti) * 1e12), color="white", fontsize=8, ha="center",
                    bbox=dict(fc="black", ec="none", pad=1))
    for g in np.arange(0, tend + 1e-15, step):
        ax.text(px(g), y1 + 12, ("%g" % (g * 1e9)), ha="center", va="center", fontsize=8)
    ax.text(x1, y1 + 28, "Time (ns)", ha="right", va="center", fontsize=8)
    px0 = 1328; R(px0, 28, 272, 800, fc="#efefef", ec="#bdbdbd")
    ax.text(px0 + 10, 48, "Display", fontsize=8.5, weight="bold")
    for i, t in enumerate(["Delay", "Max value"]):
        R(px0 + 12, 66 + i * 22, 12, 12, fc="white", ec="#555"); ax.text(px0 + 15, 73 + i * 22, "✓", fontsize=8, va="center")
        ax.text(px0 + 32, 73 + i * 22, t, fontsize=8.5, va="center")
    ax.text(px0 + 12, 125, "between:", fontsize=8.5); R(px0 + 12, 135, 110, 20, fc="white", ec="#777"); ax.text(px0 + 18, 145, rows[0][0], fontsize=8, va="center")
    ax.text(px0 + 12, 172, "and:", fontsize=8.5); R(px0 + 12, 182, 110, 20, fc="white", ec="#777"); ax.text(px0 + 18, 192, outs[0], fontsize=8, va="center")
    ax.text(px0 + 12, 232, "Evaluate", fontsize=8.5, weight="bold")
    for i, t in enumerate(["Maximum", "Frequency"]):
        R(px0 + 12, 250 + i * 22, 12, 12, fc="white", ec="#555"); ax.text(px0 + 32, 257 + i * 22, t, fontsize=8.5, va="center")
    R(px0 + 12, 305, 60, 20, fc="#dcdcdc", ec="#777"); ax.text(px0 + 30, 315, "FFT", fontsize=8.5, va="center")
    ax.text(px0 + 12, 350, "Time Scale", fontsize=8.5); R(px0 + 12, 360, 70, 20, fc="white", ec="#777")
    ax.text(px0 + 12, 400, "Step (ps)", fontsize=8.5); R(px0 + 12, 410, 70, 20, fc="white", ec="#777"); ax.text(px0 + 18, 420, "0.300", fontsize=8, va="center")
    ax.text(px0 + 12, 452, "Load: %s" % ("30 fF on outputs" if cap else "none (parasitics only)"), fontsize=8.5, color="#a00000" if cap else "#006000")
    for i, t in enumerate(["Reset", "More", "Close", "Print"]):
        R(px0 + 12, 500 + i * 34, 90, 26, fc="#e4e4e4", ec="#888"); ax.text(px0 + 57, 513 + i * 34, t, fontsize=9, ha="center", va="center")
    ax.text(px0 + 12, 650, "VDD = %.2f V" % VDD, fontsize=8.5)
    tabs = ["Voltage vs time", "Voltages and currents", "Voltage vs. voltage", "Frequency vs time", "Eye diagram"]
    xx = x0
    for i, t in enumerate(tabs):
        w = 8.2 * len(t) + 18
        R(xx, 842, w, 22, fc="white" if i == 0 else "#dcdcdc", ec="#888"); ax.text(xx + 9, 853, t, fontsize=8.5, va="center"); xx += w
    fig.savefig(out, dpi=100, facecolor="white"); plt.close(fig)


# ------------------------------------------------------------------ cases
CAP = 30e-15
CASES = {  # key: (runner, rows, outputs, tend, msk name)
    "inverter": (run_inv, [("a", "clock1"), ("y", "s1")], ["y"], 6.5e-9, "INVERTER.MSK"),
    "nand": (lambda cl: run_gate("nand", cl), [("a", "a"), ("b", "b"), ("y", "y")], ["y"], 5e-9, "NAND.MSK"),
    "nor": (lambda cl: run_gate("nor", cl), [("a", "a"), ("b", "b"), ("y", "y")], ["y"], 5e-9, "NOR.MSK"),
    "halfadder": (run_ha, [("a", "a"), ("b", "b"), ("s", "sum"), ("co", "carry")], ["s", "co"], 8e-9, "HALFADDER.MSK"),
    "mux_gates": (lambda cl: run_mux("gates", cl), [("s", "s"), ("d1", "d1"), ("d0", "d0"), ("y", "y")], ["y"], 12e-9, "MUX_GATES.MSK"),
    "mux_tg": (lambda cl: run_mux("tg", cl), [("s", "s"), ("d1", "d1"), ("d0", "d0"), ("y", "y")], ["y"], 12e-9, "MUX.MSK"),
    "sram": (run_sram, [("wl", "wl"), ("bl", "bl"), ("blb", "blb"), ("q", "q"), ("qb", "qb")], ["q", "qb"], 8.5e-9, "SRAM.MSK"),
}


def metrics(key, a, b):
    """Edge times (ps) without / with load for the document tables."""
    et = lambda t, node, rise, start: edge_times(t["t"], t[node], rise, start)
    f = lambda v: "-" if v is None else "%d ps" % round(v * 1e12)
    spec = {"inverter": [("Output rise", "y", True, 2.4e-9), ("Output fall", "y", False, 1.4e-9)],
            "nand": [("Output rise", "y", True, 3.5e-9), ("Output fall", "y", False, 2.9e-9)],
            "nor": [("Output rise", "y", True, 3.5e-9), ("Output fall", "y", False, 0.8e-9)],
            "halfadder": [("Sum rise", "s", True, 2.0e-9), ("Sum fall", "s", False, 4.0e-9), ("Carry rise", "co", True, 6.0e-9)]}[key]
    rows = [[lab, f(et(a, n, r, s)), f(et(b, n, r, s))] for lab, n, r, s in spec]
    if key == "inverter":
        for lab, ir, orr, s in (("Delay tPHL", True, False, 1.4e-9), ("Delay tPLH", False, True, 2.4e-9)):
            rows.append([lab, f(delay(a["t"], a["a"], a["y"], ir, orr, s)), f(delay(b["t"], b["a"], b["y"], ir, orr, s))])
    return [["Edge", "No capacitance", "30 fF capacitance"]] + rows


# ------------------------------------------------------------------ documents
def title(d, t): r = d.add_paragraph().add_run(t); r.bold = True; r.font.size = Pt(16)
def head(d, t): d.add_paragraph().add_run(t).bold = True
def italic(d, t): d.add_paragraph().add_run(t).italic = True
def bullet(d, t): d.add_paragraph(t, style="List Bullet")
def pic(d, png, cap):
    d.add_picture(png, width=Cm(16)); d.paragraphs[-1].alignment = 1
    r = d.add_paragraph().add_run(cap); r.italic = True; r.font.size = Pt(9); d.paragraphs[-1].alignment = 1
def table(d, rows):
    t = d.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"
    for i, r in enumerate(rows):
        for j, v in enumerate(r): t.cell(i, j).text = v
    d.add_paragraph()


GATES = {  # key: (file label, msk, sim key, aim, device table, comments)
    "not": ("NOT Gate (CMOS Inverter)", "NOT", "inverter", "Aim: CMOS inverter at 120 nm, VDD = 1.2 V; layout in Microwind and transient with and without a load capacitance.",
            [["Device", "Type", "D", "G", "S", "W/L"], ["M1", "PMOS", "out", "in", "VDD", "2"], ["M2", "NMOS", "out", "in", "GND", "1"]],
            ["Equal rise and fall times because the PMOS is 2x wider.", "The 30 fF load slows each edge about 10x (t ~ 2.2 RC)."]),
    "nand": ("NAND Gate", "NAND", "nand", "Aim: 2-input CMOS NAND at 120 nm, VDD = 1.2 V; layout in Microwind and transient with and without a load capacitance.",
             [["Device", "Type", "D", "G", "S", "W/L"], ["M1", "PMOS", "out", "A", "VDD", "2"], ["M2", "PMOS", "out", "B", "VDD", "2"],
              ["M3", "NMOS", "out", "A", "x", "2"], ["M4", "NMOS", "x", "B", "GND", "2"]],
             ["Output falls only when A = B = 1, through two series NMOS (slowest edge).", "The load slows every edge about 10x."]),
    "nor": ("NOR Gate", "NOR", "nor", "Aim: 2-input CMOS NOR at 120 nm, VDD = 1.2 V; layout in Microwind and transient with and without a load capacitance.",
            [["Device", "Type", "D", "G", "S", "W/L"], ["M1", "PMOS", "x", "A", "VDD", "4"], ["M2", "PMOS", "out", "B", "x", "4"],
             ["M3", "NMOS", "out", "A", "GND", "1"], ["M4", "NMOS", "out", "B", "GND", "1"]],
            ["Output rises only when A = B = 0, through two series PMOS (sized 4x).", "The load slows every edge about 10x."]),
    "halfadder": ("Half Adder", "HALFADDER", "halfadder", "Aim: CMOS half adder (Sum = A xor B from 4 NAND, Carry = A and B from NAND + inverter) at 120 nm, VDD = 1.2 V.",
                  None, ["Sum and Carry are correct for all four input pairs, with and without load.", "The 30 fF load slows the outputs about 10x."])}
RES = {}


def build_exp06(exp):
    img = os.path.join(exp, "img"); out = []
    for gk, (label, msk, key, aim, devs, comments) in GATES.items():
        a, b = RES[key]
        d = Document(); title(d, "VLSI D&T EXP 06 - %s" % label); italic(d, aim)
        if devs: head(d, "Circuit"); table(d, devs)
        head(d, "Layout (Microwind)")
        pic(d, os.path.join(img, "microwind_%s.png" % msk.lower()), "Layout view of %s.MSK in Microwind." % msk)
        head(d, "Simulation without capacitance")
        pic(d, os.path.join(img, "wave_%s_nocap.png" % key), "Analog simulation, no load capacitance.")
        head(d, "Simulation with capacitance")
        pic(d, os.path.join(img, "wave_%s_cap.png" % key), "Analog simulation with a 30 fF load capacitance on the output.")
        head(d, "Output"); italic(d, "Transistor-level transient, VDD = 1.2 V. Rise/fall = 10-90 %."); table(d, metrics(key, a, b))
        head(d, "Comments")
        for c in comments: bullet(d, c)
        path = os.path.join(exp, "VLSI D&T EXP 06 - %s.docx" % label); d.save(path); out.append(path)
    return out


def swap_waves(path, mapping):
    """Replace each transient image + its caption: mapping {caption text: [(png, new caption), ...]}."""
    d = Document(path); ps = list(d.paragraphs); NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}blip"
    for i, p in enumerate(ps[:-1]):
        if p._p.findall(".//" + NS) and ps[i + 1].text.strip() in mapping:
            anchor = p._p
            for png, cap in mapping[ps[i + 1].text.strip()]:
                d.add_picture(png, width=Cm(16)); p1 = d.paragraphs[-1]; p1.alignment = 1
                r = d.add_paragraph().add_run(cap); r.italic = True; r.font.size = Pt(9); p2 = d.paragraphs[-1]; p2.alignment = 1
                anchor.addprevious(p1._p); anchor.addprevious(p2._p)
            ps[i + 1]._p.getparent().remove(ps[i + 1]._p); p._p.getparent().remove(p._p)
    d.save(path)


if __name__ == "__main__":
    e = {n: glob.glob("EXP %s*" % n)[0] for n in ("06", "07", "08")}
    place = {"inverter": "06", "nand": "06", "nor": "06", "halfadder": "06", "mux_gates": "07", "mux_tg": "07", "sram": "08"}
    for key, (runner, rows, outs, tend, msk) in CASES.items():
        a, b = runner(0), runner(CAP); RES[key] = (a, b)
        for tr, cap, tag in ((a, False, "nocap"), (b, True, "cap")):
            window(tr, rows, outs, tend, msk, os.path.join(e[place[key]], "img", "wave_%s_%s.png" % (key, tag)), cap)
    for m in ("NOT", "NAND", "NOR", "HALFADDER"):
        render_layout(os.path.join("Microwind_exp", m + ".MSK"), os.path.join(e["06"], "img", "microwind_%s.png" % m.lower()))
    docs = build_exp06(e["06"])
    i7 = lambda k, t: os.path.join(e["07"], "img", "wave_%s_%s.png" % (k, t))
    i8 = lambda k, t: os.path.join(e["08"], "img", "wave_%s_%s.png" % (k, t))
    d7 = glob.glob(os.path.join(e["07"], "VLSI D&T EXP 07*.docx"))[0]; d8 = glob.glob(os.path.join(e["08"], "VLSI D&T EXP 08*.docx"))[0]
    d = Document(d7); keys = ["mux_gates", "mux_tg"]; names = ["Logic-gate MUX", "TG MUX"]
    idx = [i for i, p in enumerate(d.paragraphs) if p.text.strip() == "Transient"]
    for i, k in zip(idx, keys): d.paragraphs[i].text = "Transient " + k      # unique captions so the swap can tell them apart
    d.save(d7)
    swap_waves(d7, {"Transient " + k: [(i7(k, "nocap"), "%s: no load capacitance." % n), (i7(k, "cap"), "%s: 30 fF load capacitance." % n)]
                    for k, n in zip(keys, names)})
    swap_waves(d8, {"Write 1 (1-3 ns), read (5-6 ns), write 0 (6.5-8 ns)": [(i8("sram", "nocap"), "6T SRAM: no bit-line capacitance."),
                                                                         (i8("sram", "cap"), "6T SRAM: 30 fF bit-line capacitance.")]})
    print("\n".join(docs + [d7, d8]))
