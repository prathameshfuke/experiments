"""Render VCD files from NVC simulations as waveform PNGs (Vivado-style dark theme)."""
import re, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def read_vcd(path, scope_name):
    """Return {signal: [(time_ns, value_str)]} for signals directly in `scope_name`, plus end time."""
    ids, cur, depth_scope, data, t = {}, [], None, {}, 0
    tscale = 1e-6  # fs -> ns
    in_target = False
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("$scope"):
                name = line.split()[2]
                cur.append(name)
                in_target = (len(cur) == 1 and name == scope_name)
            elif line.startswith("$upscope"):
                cur.pop(); in_target = False
            elif line.startswith("$var") and in_target:
                p = line.split(); ids[p[3]] = re.sub(r"\[.*\]", "", p[4]); data[ids[p[3]]] = []
            elif line.startswith("#"):
                t = int(line[1:]) * tscale
            elif line and line[0] in "01xXzZ" and line[1:] in ids:
                data[ids[line[1:]]].append((t, line[0]))
            elif line.startswith("b"):
                v, i = line[1:].split()
                if i in ids: data[ids[i]].append((t, v))
    return data, t

def fmt(v, radix, width):
    if "x" in v.lower() or "u" in v.lower(): return "X"
    n = int(v, 2)
    return {"h": f"{n:X}", "d": str(n), "b": v.zfill(width)}[radix]

def draw(path, scope, spec, out, tmax=None, title=None, cursor_label=True):
    data, tend = read_vcd(path, scope)
    tmax = tmax or tend
    fig, ax = plt.subplots(figsize=(11, 0.55 * len(spec) + 1.2), facecolor="#1e1e1e")
    ax.set_facecolor("#000000")
    for k, (sig, radix, label) in enumerate(spec):
        y0 = len(spec) - 1 - k
        ev = data[sig] + [(tmax, None)]
        first = ev[0][1]
        is_bus = len(first) > 1 or radix != "bit"
        for (t1, v), (t2, _) in zip(ev, ev[1:]):
            t2 = min(t2, tmax)
            if t1 >= tmax: break
            if not is_bus:
                lvl = 0.8 if v == "1" else 0.1
                ax.plot([t1, t2], [y0 + lvl] * 2, color="#3cff3c", lw=1.6)
                if t2 < tmax:
                    nxt = [x for x in ev if x[0] == t2][0][1]
                    if nxt is not None and nxt != v:
                        ax.plot([t2, t2], [y0 + 0.1, y0 + 0.8], color="#3cff3c", lw=1.6)
            else:
                ax.plot([t1, t2], [y0 + 0.1] * 2, color="#3cff3c", lw=1.2)
                ax.plot([t1, t2], [y0 + 0.8] * 2, color="#3cff3c", lw=1.2)
                ax.plot([t1, t1], [y0 + 0.1, y0 + 0.8], color="#3cff3c", lw=1.2)
                ax.plot([t2, t2], [y0 + 0.1, y0 + 0.8], color="#3cff3c", lw=1.2)
                if (t2 - t1) > 0.012 * tmax:
                    ax.text((t1 + t2) / 2, y0 + 0.45, fmt(v, radix if radix != "bit" else "b", len(v)),
                            color="#ffff66", ha="center", va="center", fontsize=8.5, family="monospace")
        ax.text(-0.01 * tmax, y0 + 0.45, label, color="#e6e6e6", ha="right", va="center", fontsize=9, family="monospace")
        ax.axhline(y0, color="#333333", lw=0.5)
    ax.set_xlim(0, tmax); ax.set_ylim(0, len(spec))
    step = next(s for s in [5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000] if tmax / s <= 14)
    ax.set_xticks(range(0, int(tmax) + 1, step)); ax.set_yticks([])
    ax.tick_params(colors="#cccccc", labelsize=8); ax.grid(axis="x", color="#2a2a2a", lw=0.6)
    for s in ax.spines.values(): s.set_color("#555555")
    ax.set_xlabel("time (ns)", color="#cccccc", fontsize=9)
    if title: ax.set_title(title, color="#ffffff", fontsize=10)
    fig.subplots_adjust(left=0.13, right=0.99, top=0.9 if title else 0.97, bottom=0.14)
    fig.savefig(out, dpi=150, facecolor=fig.get_facecolor()); plt.close(fig)

if __name__ == "__main__":
    S = "../sim/"; I = "../img/"
    draw(S+"alu4bit.vcd", "alu4bit_tb",
         [("a","d","A[3:0]"),("b","d","B[3:0]"),("s","b","S[2:0]"),("y","d","Y[3:0]")],
         I+"exp1_wave.png", title="Exp 1: 4-bit ALU simulation (values in decimal, S in binary)")
    draw(S+"usr.vcd", "usr_tb",
         [("clk","bit","clk"),("s","b","S[1:0]"),("il","bit","IL"),("ir","bit","IR"),("p","b","P[3:0]"),("q","b","Q[3:0]")],
         I+"exp2_wave.png", title="Exp 2: Universal shift register simulation")
    draw(S+"updown_counter.vcd", "updown_counter_tb",
         [("clk","bit","clk"),("rst","bit","rst"),("en","bit","en"),("up","bit","up"),("qout","d","Qout[3:0]")],
         I+"exp3_wave.png", title="Exp 3: 4-bit up/down counter simulation (Qout in decimal)")
    draw(S+"fifo.vcd", "fifo_tb",
         [("clk","bit","clk"),("reset","bit","reset"),("w","bit","w"),("r","bit","r"),("d","h","d[7:0]"),
          ("q","h","q[7:0]"),("empty","bit","empty"),("full","bit","full")],
         I+"exp4_wave.png", title="Exp 4: FIFO simulation (d and q in hex)")
    draw(S+"keypad.vcd", "keypad_tb",
         [("row","b","row[3:0]"),("col","b","col[3:0]"),("led","h","led[15:0]"),("hex","h","hex[3:0]")],
         I+"exp5_wave.png", tmax=1250, title="Exp 5: Keypad scanner simulation (key 0 then key 5 pressed; SCAN_DIV = 4)")
