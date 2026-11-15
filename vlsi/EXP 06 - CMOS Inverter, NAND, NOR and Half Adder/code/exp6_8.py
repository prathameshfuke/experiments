"""EXP 06 - Inverter, NAND, NOR, Half Adder

Python simulation (optional):  python3 exp6_8.py   (needs numpy + matplotlib) -> img/*.png, sim/results.json

DSCH: File > New. Symbol palette: place Inverter (then NAND2, NOR2), a Clock input and an LED output.
       Half adder: one XOR2 (Sum) and one AND2 (Carry), inputs A and B, two LEDs.
       Simulate > Start Simulation, check the truth table, then Make Verilog File.

TOOLS: DSCH 3.1 (logic/schematic) and Microwind 3.1 (layout + simulation), same installer package.
SETUP
 1. Microwind: File > Select Foundry > cmos012.rul  (120 nm, VDD = 1.2 V, lambda = 0.06 um).
 2. DSCH: draw and check the logic first (steps below), then File > Make Verilog File.
 3. Microwind: Compile > Compile Verilog File > pick that file. The layout is generated.
    (Or draw by hand: Palette > nMOS / pMOS, poly, contacts, metal1; draw Vdd and Vss rails.)
 4. Simulate > Run Simulation. Tick Voltage/Time, select the nodes to plot.
 5. WITHOUT load: screenshot, read rise/fall time between 10% and 90% of 1.2 V on the output.
 6. WITH load: add a capacitor (~30 fF) on the output node, run again, screenshot, compare.
 7. Comment: load increases rise and fall times (t ~ 2.2 R C).
Menu names are from Microwind/DSCH 3.1 and may differ slightly in your version.
"""
import json
from cmos import *

I = "img/"
res = {}

def inv(c, a, y, vdd="vdd", gnd="gnd"):
    c.p(y, a, vdd); c.n(y, a, gnd)
def nand(c, a, b, y, tag):
    m = f"{tag}_m"
    c.p(y, a, "vdd"); c.p(y, b, "vdd"); c.n(y, a, m, 2); c.n(m, b, "gnd", 2)
def nor(c, a, b, y, tag):
    m = f"{tag}_m"
    c.p(m, a, "vdd", 4); c.p(y, b, m, 4); c.n(y, a, "gnd"); c.n(y, b, "gnd")
def rails(c):
    c.drive("vdd", lambda t: VDD); c.drive("gnd", lambda t: 0.0)

def load(c, node, cl):
    c.node(node, CPAR + cl)

def level_at(tr, name, t):
    return tr[name][int(t / DT)] > VDD / 2

# ---------------- Experiment 6 ----------------
T = 1.0e-9
def run_inv(cl):
    c = Circuit(); rails(c); load(c, "y", cl); inv(c, "a", "y")
    c.drive("a", pulse_seq([0, 1, 0], T, t0=0.5e-9)); return c.run(3.0e-9)
a, b = run_inv(0), run_inv(CLOAD)
plot({"without load": a, "with load": b}, ["a", "y"], I + "exp6_inverter.png", "Inverter transient: input a, output y", 3.0e-9)
res["inverter"] = {k: dict(tr=edge_times(t["t"], t["y"], True, 1.4e-9), tf=edge_times(t["t"], t["y"], False, 0.4e-9),
                           tphl=delay(t["t"], t["a"], t["y"], True, False, 0.4e-9),
                           tplh=delay(t["t"], t["a"], t["y"], False, True, 1.4e-9))
                   for k, t in {"without load": a, "with load": b}.items()}

def run_gate(kind, cl):
    c = Circuit(); rails(c); load(c, "y", cl)
    (nand if kind == "nand" else nor)(c, "a", "b", "y", "g")
    c.drive("a", pulse_seq([0, 0, 1, 1, 0], 1e-9)); c.drive("b", pulse_seq([0, 1, 0, 1, 0], 1e-9))
    return c.run(5.0e-9)
for kind in ("nand", "nor"):
    a, b = run_gate(kind, 0), run_gate(kind, CLOAD)
    for lab, t in (("without load", a), ("with load", b)):
        for k, (x, y) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):   # check truth table after settling
            tt = (k * 1e-9) + 0.95e-9
            exp = (not (x and y)) if kind == "nand" else (not (x or y))
            assert level_at(t, "y", tt) == exp, (kind, lab, x, y)
    plot({"without load": a, "with load": b}, ["a", "b", "y"], I + f"exp6_{kind}.png",
         f"{kind.upper()}2 transient: inputs a, b and output y", 5.0e-9)
    # output falls when both inputs high (NAND) / output rises when last input falls (NOR)
    if kind == "nand":
        meas = lambda t: dict(tf=edge_times(t["t"], t["y"], False, 2.9e-9), tr=edge_times(t["t"], t["y"], True, 3.5e-9))
    else:
        meas = lambda t: dict(tf=edge_times(t["t"], t["y"], False, 0.8e-9), tr=edge_times(t["t"], t["y"], True, 3.5e-9))
    res[kind] = {"without load": meas(a), "with load": meas(b)}

def run_ha(cl):
    c = Circuit(); rails(c); load(c, "s", cl); load(c, "co", cl)
    nand(c, "a", "b", "n1", "h1"); nand(c, "a", "n1", "n2", "h2"); nand(c, "b", "n1", "n3", "h3")
    nand(c, "n2", "n3", "s", "h4")                       # sum = a xor b
    nand(c, "a", "b", "n5", "h5"); inv(c, "n5", "co")    # carry = a and b
    c.drive("a", pulse_seq([0, 0, 1, 1], 2e-9)); c.drive("b", pulse_seq([0, 1, 0, 1], 2e-9))
    return c.run(8.0e-9)
a, b = run_ha(0), run_ha(CLOAD)
for lab, t in (("without load", a), ("with load", b)):
    for k, (x, y) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
        tt = k * 2e-9 + 1.9e-9
        assert level_at(t, "s", tt) == bool(x ^ y) and level_at(t, "co", tt) == bool(x & y), ("ha", lab, x, y)
plot({"without load": a, "with load": b}, ["a", "b", "s", "co"], I + "exp6_halfadder.png",
     "Half adder transient: inputs a, b, outputs sum s and carry co", 8.0e-9)
res["halfadder"] = {k: dict(sum_tr=edge_times(t["t"], t["s"], True, 2.0e-9), sum_tf=edge_times(t["t"], t["s"], False, 4.0e-9),
                            carry_tr=edge_times(t["t"], t["co"], True, 6.0e-9))
                    for k, t in {"without load": a, "with load": b}.items()}

# ---------------- Experiment 7 ----------------
def run_mux(kind, cl):
    c = Circuit(); rails(c); load(c, "y", cl)
    if kind == "gates":
        inv(c, "s", "sb"); nand(c, "d1", "s", "n1", "m1"); nand(c, "d0", "sb", "n2", "m2"); nand(c, "n1", "n2", "y", "m3")
    else:
        inv(c, "s", "sb")
        c.tg("d0", "y", "sb", "s"); c.tg("d1", "y", "s", "sb")
        c.init["y"] = 0.0
    # sequence of (s, d1, d0): select d0 first, then d1
    seq = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
    step = 1.5e-9
    for idx, name in enumerate(("s", "d1", "d0")):
        c.drive(name, pulse_seq([q[idx] for q in seq], step, tedge=30e-12))
    t = c.run(len(seq) * step); t["seq"] = seq; t["step"] = step; return t
for kind in ("gates", "tg"):
    a, b = run_mux(kind, 0), run_mux(kind, CLOAD)
    for lab, t in (("without load", a), ("with load", b)):
        for k, (s, d1, d0) in enumerate(t["seq"]):
            assert level_at(t, "y", (k + 1) * t["step"] - 0.05e-9) == bool(d1 if s else d0), ("mux", kind, lab, k)
    plot({"without load": a, "with load": b}, ["s", "d1", "d0", "y"], I + f"exp7_mux_{kind}.png",
         f"2:1 mux using {'logic gates' if kind == 'gates' else 'transmission gates'}: select s, data d1, d0, output y", len(a["seq"]) * a["step"])
    # y rises when d0 goes 0->1 with s=0 (step 1), y falls when d0 goes 1->0 with s=0 (step 2)
    meas = lambda t: dict(tr=edge_times(t["t"], t["y"], True, 1.5e-9), tf=edge_times(t["t"], t["y"], False, 3.0e-9))
    res["mux_" + kind] = {"without load": meas(a), "with load": meas(b)}

# ---------------- Experiment 8 ----------------
def run_sram(cl):
    c = Circuit(); rails(c)
    # latch: two cross-coupled inverters (q, qb); pull-up beta is small so the access transistors win a write
    c.node("q", v0=0.0); c.node("qb", v0=VDD)
    c.p("q", "qb", "vdd", 1.0);  c.n("q", "qb", "gnd", 3.0)
    c.p("qb", "q", "vdd", 1.0);  c.n("qb", "q", "gnd", 3.0)
    c.n("bl", "wl", "q", 2.0);   c.n("blb", "wl", "qb", 2.0)
    c.node("bl", CPAR + cl); c.node("blb", CPAR + cl)
    n = 1e-9
    # 0-1 ns hold (state 0) | 1-3 ns write 1 | 3-4 ns hold | 4-6 ns read (bitlines precharged, then floating) | 6-8 ns write 0
    c.drive("wl", pwl([(0, 0), (1*n, 0), (1.03*n, VDD), (3*n, VDD), (3.03*n, 0), (5*n, 0), (5.03*n, VDD), (6*n, VDD), (6.03*n, 0),
                       (6.5*n, 0), (6.53*n, VDD), (8*n, VDD), (8.03*n, 0)]))
    def bl(t):
        if 1e-9 <= t < 3e-9: return VDD
        if 4e-9 <= t < 5e-9: return VDD          # precharge
        if 5e-9 <= t < 6e-9: return None          # float during read
        if 6.5e-9 <= t < 8e-9: return 0.0
        return 0.0 if t < 1e-9 else None
    def blb(t):
        if 1e-9 <= t < 3e-9: return 0.0
        if 4e-9 <= t < 5e-9: return VDD
        if 5e-9 <= t < 6e-9: return None
        if 6.5e-9 <= t < 8e-9: return VDD
        return VDD if t < 1e-9 else None
    c.drive("bl", bl); c.drive("blb", blb)
    c.init["bl"] = VDD * 0; c.init["blb"] = VDD
    return c.run(8.5e-9)
a, b = run_sram(0), run_sram(30e-15)
for lab, t in (("without load", a), ("with load", b)):
    assert level_at(t, "q", 2.9e-9) and not level_at(t, "qb", 2.9e-9), ("sram write 1", lab)
    assert level_at(t, "q", 4.5e-9) and not level_at(t, "qb", 4.5e-9), ("sram hold 1", lab)
    assert level_at(t, "q", 5.9e-9), ("sram read keeps 1", lab)
    assert not level_at(t, "q", 8.4e-9) and level_at(t, "qb", 8.4e-9), ("sram write 0", lab)
plot({"without load": a, "with load": b}, ["wl", "bl", "blb", "q", "qb"], I + "exp8_sram.png",
     "6T SRAM cell: write 1, hold, read, write 0", 8.5e-9)
res["sram"] = {k: dict(write1_q_rise=edge_times(t["t"], t["q"], True, 1.0e-9), write0_q_fall=edge_times(t["t"], t["q"], False, 6.5e-9),
                       read_blb_delay=cross(t["t"], t["blb"], VDD / 2, False, 5.0e-9) - 5.015e-9)
               for k, t in {"without load": a, "with load": b}.items()}

json.dump(res, open("sim/results.json", "w"), indent=1, default=lambda x: None if x is None else float(x))
print(json.dumps(res, indent=1, default=float))
