"""Small transistor-level transient simulator (Level-1 MOSFET, explicit Euler).
Used to produce the Part B timing results because Microwind is not available here.
Technology figures follow the manual: 120 nm, VDD = 1.2 V, lambda = 0.06 um."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

VDD, VT = 1.2, 0.4
KN, KP = 4.0e-4, 2.0e-4     # beta of a W/L = 1 device (A/V^2); PMOS is ~half as strong
CPAR = 2e-15                # parasitic capacitance on every node (F)
CLOAD = 30e-15              # output load used for the "with capacitive load" runs
DT = 0.25e-12

def _ids_n(vd, vg, vs, beta):
    if vd < vs:
        return -_ids_n(vs, vg, vd, beta)
    vov, vds = vg - vs - VT, vd - vs
    if vov <= 0: return 0.0
    return beta * (vov * vds - vds * vds / 2) if vds < vov else beta * vov * vov / 2

def pwl(points):
    """Piece-wise linear source from [(t, v), ...] (times in seconds)."""
    ts, vs = zip(*points)
    return lambda t: float(np.interp(t, ts, vs))

def pulse_seq(levels, tstep, tedge=30e-12, t0=0.0):
    """Source that steps through `levels` (0/1) every `tstep` seconds."""
    pts = [(0, levels[0] * VDD)]
    for k in range(1, len(levels)):
        if levels[k] != levels[k - 1]:
            t = t0 + k * tstep
            pts += [(t, levels[k - 1] * VDD), (t + tedge, levels[k] * VDD)]
    pts.append((1.0, levels[-1] * VDD))
    return pwl(pts)

class Circuit:
    def __init__(self):
        self.dev, self.cap, self.src, self.init = [], {}, {}, {}
    def node(self, name, c=CPAR, v0=0.0):
        self.cap[name] = self.cap.get(name, 0) + c; self.init[name] = v0
    def n(self, d, g, s, w=1.0): self.dev.append(("n", d, g, s, KN * w))
    def p(self, d, g, s, w=2.0): self.dev.append(("p", d, g, s, KP * w))
    def tg(self, a, b, g, gb, wn=1.0, wp=2.0):
        self.n(a, g, b, wn); self.p(a, gb, b, wp)
    def drive(self, name, f): self.src[name] = f          # f(t) -> volts, or None = released (floating)
    def run(self, tend):
        names = list(self.cap)
        for d in self.dev:
            for x in d[1:4]:
                if x not in self.cap and x not in self.src: self.node(x)
        names = list(self.cap)
        v = {n: self.init[n] for n in names}
        steps = int(tend / DT)
        tr = {n: np.zeros(steps) for n in list(names) + list(self.src)}
        for k in range(steps):
            t = k * DT
            for s, f in self.src.items():
                val = f(t)
                if val is not None: v[s] = val
                elif s not in v: v[s] = 0.0
            cur = {n: 0.0 for n in names}
            for kind, d, g, s, beta in self.dev:
                vd, vg, vs = v[d], v[g], v[s]
                i = _ids_n(vd, vg, vs, beta) if kind == "n" else -_ids_n(VDD - vd, VDD - vg, VDD - vs, beta)
                if d in cur: cur[d] -= i
                if s in cur: cur[s] += i
            for n in names:
                driven = n in self.src and self.src[n](t) is not None
                if not driven: v[n] += cur[n] * DT / self.cap[n]
            for n in tr: tr[n][k] = v.get(n, 0.0)
        tr["t"] = np.arange(steps) * DT
        return tr

def cross(t, y, level, rising, start=0.0):
    """First time after `start` that y crosses `level` going up (rising) or down."""
    i0 = int(start / DT)
    for i in range(max(i0, 1), len(y)):
        if (rising and y[i - 1] < level <= y[i]) or (not rising and y[i - 1] > level >= y[i]):
            return t[i - 1] + (level - y[i - 1]) / (y[i] - y[i - 1]) * DT
    return None

def edge_times(t, y, rising, start):
    """10-90 % (rising) or 90-10 % (falling) transition time of the first output edge after `start`."""
    lo, hi = 0.1 * VDD, 0.9 * VDD
    a = cross(t, y, lo if rising else hi, rising, start)
    b = cross(t, y, hi if rising else lo, rising, a) if a is not None else None
    return None if b is None else b - a

def delay(t, vin, vout, in_rising, out_rising, start):
    a = cross(t, vin, VDD / 2, in_rising, start)
    b = cross(t, vout, VDD / 2, out_rising, a or start)
    return None if a is None or b is None else b - a

def plot(traces_by_case, rows, out, title, tmax):
    """traces_by_case: {label: trace dict}; rows: list of node names, drawn one axis per node."""
    fig, axs = plt.subplots(len(rows), 1, figsize=(10, 1.3 * len(rows) + 0.8), sharex=True)
    colors = {"without load": "#1f77b4", "with load": "#d62728"}
    for ax, name in zip(axs, rows):
        for lab, tr in traces_by_case.items():
            ax.plot(tr["t"] * 1e9, tr[name], color=colors.get(lab, "#444444"), lw=1.5, label=lab)
        ax.set_ylabel(name + " (V)", fontsize=9); ax.set_ylim(-0.1, VDD + 0.15); ax.grid(alpha=0.3)
        ax.set_yticks([0, 0.6, 1.2])
    axs[0].legend(loc="upper right", fontsize=8, ncol=2); axs[0].set_title(title, fontsize=10)
    axs[-1].set_xlabel("time (ns)"); axs[-1].set_xlim(0, tmax * 1e9)
    fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)
