"""Build the 'Viva Explanations' pages and insert them after page 19 of the VLSI D&T study notes.
Run from the repo root:  python3 vlsi/tools/viva_notes.py
Reads PNGs from vlsi/gate_diagrams, vlsi/viva_images and the EXP img/ folders; rewrites the three study-notes PDFs.
Numbers for the CMOS gates come from our own transistor-level simulation (120 nm, VDD = 1.2 V), not from Microwind."""
import glob, os, shutil, sys, tempfile
import pypdf
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

V = "vlsi/"
NOTES_DIR = "study_notes/"
BASE = NOTES_DIR + "VLSI D&T Study Notes.pdf"
BASE_PAGES = 19   # 14 notes pages + 5 diagram pages; the viva pages are appended after them

INK = colors.HexColor("#0e1726")
BLUE = colors.HexColor("#2547f5")
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=15, leading=19, spaceBefore=2, spaceAfter=5, textColor=INK)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15, spaceBefore=9, spaceAfter=3, textColor=BLUE, keepWithNext=1)
B = ParagraphStyle("b", fontName="Helvetica", fontSize=9.4, leading=12.6, spaceAfter=3)
BL = ParagraphStyle("bl", parent=B, leftIndent=12, bulletIndent=2, spaceAfter=1.5)
Q = ParagraphStyle("q", parent=B, fontName="Helvetica-Bold", spaceBefore=3, spaceAfter=0, keepWithNext=1)
A = ParagraphStyle("a", parent=B, leftIndent=12, spaceAfter=2)
CAP = ParagraphStyle("c", parent=B, fontSize=8.2, leading=10.5, alignment=1, textColor=colors.HexColor("#444444"))
SM = ParagraphStyle("sm", parent=B, fontSize=8.4, leading=11)
TC = ParagraphStyle("tc", parent=B, fontSize=8.4, leading=10.6, spaceAfter=0)
TH = ParagraphStyle("th", parent=TC, fontName="Helvetica-Bold")


def p(t, s=B): return Paragraph(t, s)
def bl(items): return [Paragraph(t, BL, bulletText="•") for t in items]
def qa(pairs):
    out = []
    for q, a in pairs: out += [Paragraph("Q. " + q, Q), Paragraph(a, A)]
    return out


def img(path, w, caption=None):
    iw, ih = ImageReader(path).getSize()
    items = [Image(path, width=w, height=w * ih / iw)]
    if caption: items.append(Paragraph(caption, CAP))
    return items


def side(left, right, wl=8.6 * cm, wr=9.2 * cm):
    t = Table([[left, right]], colWidths=[wl, wr])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    return t


def table(rows, widths, head=True):
    data = [[Paragraph(str(c), TH if (head and i == 0) else TC) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c0cc")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if head: st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6ebf5")))
    t.setStyle(TableStyle(st)); return t


def pair(a, b):
    t = Table([[a, b]], colWidths=[8.8 * cm, 8.8 * cm]); t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")])); return t


def exp_img(num, name): return glob.glob("%sEXP %s*/img/%s" % (V, num, name))[0]
GD = V + "gate_diagrams/"
VI = V + "viva_images/"
W17 = 15.2 * cm

S = []   # the story

# ------------------------------------------------------------------ intro
S += [p("Viva Explanations", H1),
      p("How to answer for every experiment: say the <b>aim</b> in one line, show the <b>circuit or block diagram</b>, explain <b>how it works</b>, "
        "walk through the <b>waveform</b> from left to right, then say <b>why the design is built that way</b>. The pages below follow that order. "
        "For the CMOS experiments the timing numbers come from our own transistor-level simulation (120 nm, VDD = 1.2 V); Microwind gives somewhat "
        "different values, so quote the <i>trend</i> (a load capacitor makes every edge about ten times slower) and not the exact picoseconds."),
      table([["Topic", "Pages"],
             ["1. CMOS inverter, NAND, NOR and half adder, with and without capacitive load", "6"],
             ["2. 2:1 multiplexer (gates and transmission gates) and how to draw its layout", "2"],
             ["3. 6T SRAM cell and CMOS D flip-flop", "2"],
             ["4. FPGA vs CPLD, and the FPGA design flow", "1-2"],
             ["5. VHDL experiments 1-5: what the code does, why, the waveform, viva questions", "5"],
             ["6. Why is the design like that? One-line answers", "1"]], [14 * cm, 3.4 * cm]),
      PageBreak()]

# ------------------------------------------------------------------ 1. CMOS and capacitive load
S += [p("1. CMOS Gates With and Without Capacitive Load", H1),
      p("1.1 What the examiner wants to hear", H2),
      p("A CMOS gate has a <b>pull-up network</b> of PMOS transistors to VDD and a <b>pull-down network</b> of NMOS transistors to ground. For any input, exactly "
        "one network conducts, so there is <b>no static current</b> (only leakage). The output node always has a capacitance C<sub>L</sub>: the drain and source junctions "
        "of the gate's own transistors, the wire, and the gate capacitance of every gate it drives (fan-out). "
        "<b>Without load</b> we simulate only the small parasitic capacitance of the gate itself (a few fF). <b>With load</b> we add an explicit 30 fF capacitor from the output to ground, "
        "which models a long wire or a large fan-out."),
      p("1.2 Theory: why the capacitor slows the gate", H2)]
S += bl(["A conducting transistor behaves like a resistor R<sub>on</sub>: <b>R<sub>n</sub></b> for the NMOS pull-down, <b>R<sub>p</sub></b> for the PMOS pull-up.",
         "Output <b>rising</b>: the PMOS charges C<sub>L</sub> through R<sub>p</sub>: V<sub>out</sub>(t) = VDD (1 - e<super>-t/(R<sub>p</sub>C<sub>L</sub>)</super>).",
         "Output <b>falling</b>: the NMOS discharges C<sub>L</sub> through R<sub>n</sub>: V<sub>out</sub>(t) = VDD e<super>-t/(R<sub>n</sub>C<sub>L</sub>)</super>.",
         "Propagation delay (to 50 %): <b>t<sub>pd</sub> = 0.69 R C</b>. Rise or fall time (10 % to 90 %): <b>t<sub>r</sub>, t<sub>f</sub> = 2.2 R C</b>. Delay grows in direct proportion to C.",
         "Dynamic power: <b>P = &alpha; C<sub>L</sub> VDD<super>2</super> f</b> (&alpha; = switching activity). Each full cycle takes C<sub>L</sub>VDD<super>2</super> from the supply: for 30 fF and 1.2 V that is 43 fJ.",
         "How to speed a loaded gate: make the transistors wider (smaller R, but more self-capacitance), insert a buffer or inverter chain (each stage about 4x bigger), or shorten the wire."])
S += [p("1.3 Results: without and with the 30 fF load (our simulation)", H2),
      table([["Circuit", "Edge", "No capacitance", "30 fF capacitance", "Slower by"],
             ["Inverter", "output rise / fall (10-90 %)", "22 ps / 22 ps", "321 ps / 321 ps", "about 14x"],
             ["Inverter", "delay t<sub>PHL</sub> / t<sub>PLH</sub> (50 %)", "18 ps / 18 ps", "159 ps / 159 ps", "about 9x"],
             ["NAND", "output rise / fall", "14 ps / 23 ps", "160 ps / 323 ps", "11x / 14x"],
             ["NOR", "output rise / fall", "23 ps / 22 ps", "323 ps / 321 ps", "14x / 15x"],
             ["Half adder", "sum rise / fall, carry rise", "35 / 27 / 25 ps", "333 / 325 / 321 ps", "about 10-13x"]],
            [2.3 * cm, 5.2 * cm, 3.4 * cm, 3.6 * cm, 2.9 * cm]),
      Spacer(1, 4),
      p("<b>Say it like this:</b> the output has to move charge C<sub>L</sub>V<sub>DD</sub> through a transistor resistance. A bigger C needs more time (t = RC), so every edge slows by roughly the ratio of the total capacitances, "
        "and the gate also burns more power per switch. The output edges stop being sharp and become the round shoulders of an RC charging curve.", SM),
      PageBreak()]

# ---- inverter
S += [p("1.4 CMOS Inverter (NOT)", H1)]
S += [side(img(GD + "gate_not_cl.png", 7.6 * cm, "Inverter with the load capacitor C<sub>L</sub>."),
           [table([["A", "PMOS", "NMOS", "Y"], ["0", "ON", "OFF", "1 (pulled to VDD)"], ["1", "OFF", "ON", "0 (pulled to GND)"]], [1 * cm, 1.8 * cm, 1.8 * cm, 4 * cm]),
            Spacer(1, 4)] + bl(["<b>Sizing:</b> W/L of the PMOS is 2, of the NMOS is 1. Holes move about 2-3 times slower than electrons, so the PMOS must be 2-3 times wider to give the same drive.",
                                 "<b>Result:</b> equal rise and fall times (22 ps both) and a switching threshold V<sub>M</sub> near VDD/2, which gives the best noise margin.",
                                 "<b>Voltage transfer curve:</b> flat, then a very steep drop around VDD/2 (gain much greater than 1), then flat. That steepness regenerates a weak input back to a clean 0 or 1."]))]
S += [p("Waveform: how to explain it", H2)]
S += [pair(img(exp_img("06", "wave_inverter_nocap.png"), 8.6 * cm, "Without capacitance"), img(exp_img("06", "wave_inverter_cap.png"), 8.6 * cm, "With 30 fF capacitance"))]
S += bl(["Top trace (green) is the input <b>clock1</b>, bottom trace (red) is the output <b>s1</b>. The output is the inverse of the input.",
         "Dashed vertical lines are the time grid (0.5 ns). The solid white lines mark where the input and output cross 50 %; the label (for example <b>159ps</b>) is the propagation delay between them.",
         "<b>Without load</b> the output edges are almost vertical. <b>With load</b> they curve like an exponential: the output creeps toward VDD or 0 and the delay is about ten times longer.",
         "The very first red curve starts at 0 V and rises slowly: that is the output charging from its initial state before the first input edge, not a switching delay.",
         "Both edges take the same time, which proves the 2:1 PMOS/NMOS sizing is correct."])
S += qa([("Why is the PMOS wider than the NMOS?", "Hole mobility is about half the electron mobility, so for equal current the PMOS needs about twice the W/L. This makes rise time equal to fall time."),
         ("What is the static power of the inverter?", "Almost zero. In steady state one transistor is OFF, so there is no DC path from VDD to ground; only leakage flows."),
         ("Where does the power go then?", "During switching: charging and discharging C<sub>L</sub> (dynamic power, &alpha;C<sub>L</sub>VDD<super>2</super>f) plus a short-circuit current while both transistors conduct for a moment.")])
S += [PageBreak()]

# ---- NAND
S += [p("1.5 CMOS NAND Gate", H1)]
S += [side(img(GD + "gate_nand_cl.png", 7.8 * cm, "NAND with the load capacitor."),
           [table([["A B", "Conducting transistors", "Y"], ["0 0", "both PMOS ON, NMOS chain OFF", "1"], ["0 1", "PMOS(A) ON, NMOS(A) OFF", "1"],
                   ["1 0", "PMOS(B) ON, NMOS(B) OFF", "1"], ["1 1", "both NMOS ON (series), PMOS OFF", "0"]], [1.4 * cm, 5.6 * cm, 1 * cm]),
            Spacer(1, 4)] + bl(["Y = (A.B)'. <b>Pull-down:</b> two NMOS in <b>series</b> (both must be ON for a 0). <b>Pull-up:</b> two PMOS in <b>parallel</b> (any one gives a 1). The pull-up is the dual of the pull-down.",
                                 "<b>Sizing:</b> NMOS W/L = 2 each (series pair equals one unit NMOS of the inverter), PMOS W/L = 2.",
                                 "<b>Slowest edge:</b> the falling output through the two series NMOS (23 ps vs 14 ps rising)."]))]
S += [p("Waveform: how to explain it", H2)]
S += [pair(img(exp_img("06", "wave_nand_nocap.png"), 8.6 * cm, "Without capacitance"), img(exp_img("06", "wave_nand_cap.png"), 8.6 * cm, "With 30 fF capacitance"))]
S += bl(["Inputs a and b (green) step through 00, 01, 10, 11, 00 for 1 ns each; the output y (red) is high except while <b>both</b> inputs are high (3 ns to 4 ns): that is the NAND truth table.",
         "Without load the fall at 3 ns and the rise at 4 ns are almost vertical (21 ps and 13 ps delay). With load they are slow exponentials (hundreds of ps).",
         "The small dip in y at 2 ns (without load) is a <b>glitch</b>: a rises while b falls, so for a moment both inputs are above the threshold and the NMOS chain starts to conduct. With the load capacitor the RC filter absorbs the dip.",
         "Falling takes longer than rising because two NMOS conduct in series."])
S += qa([("Why is NAND preferred over NOR in CMOS?", "NAND puts the series transistors in the NMOS network, and electrons are faster than holes. NOR needs series PMOS, which are weak, so the PMOS must be 4x wide: bigger area and more input capacitance."),
         ("Why is NAND called a universal gate?", "Any Boolean function can be built from NAND gates only (NOT = NAND with inputs tied, AND = NAND + NOT, OR = NAND of inverted inputs)."),
         ("How many transistors does a 2-input NAND need?", "Four (2 PMOS + 2 NMOS). An AND gate needs six: NAND plus an inverter.")])
S += [PageBreak()]

# ---- NOR
S += [p("1.6 CMOS NOR Gate", H1)]
S += [side(img(GD + "gate_nor_cl.png", 7.8 * cm, "NOR with the load capacitor."),
           [table([["A B", "Conducting transistors", "Y"], ["0 0", "both PMOS ON (series), NMOS OFF", "1"], ["0 1", "NMOS(B) ON, PMOS chain OFF", "0"],
                   ["1 0", "NMOS(A) ON, PMOS chain OFF", "0"], ["1 1", "both NMOS ON (parallel)", "0"]], [1.4 * cm, 5.6 * cm, 1 * cm]),
            Spacer(1, 4)] + bl(["Y = (A+B)'. <b>Pull-up:</b> two PMOS in <b>series</b> (both must be ON for a 1). <b>Pull-down:</b> two NMOS in <b>parallel</b> (any one gives a 0).",
                                 "<b>Sizing:</b> PMOS W/L = 4 each (series pair of the inverter's 2), NMOS W/L = 1.",
                                 "<b>Slowest edge:</b> the rising output through the two series PMOS (23 ps vs 22 ps)."]))]
S += [p("Waveform: how to explain it", H2)]
S += [pair(img(exp_img("06", "wave_nor_nocap.png"), 8.6 * cm, "Without capacitance"), img(exp_img("06", "wave_nor_cap.png"), 8.6 * cm, "With 30 fF capacitance"))]
S += bl(["With the same input sequence as the NAND, y is high only when <b>both</b> inputs are low (0 to 1 ns, and again from 4 ns): the NOR truth table.",
         "Any input at 1 pulls y to 0 through a parallel NMOS, so the fall is quick; the rise at 4 ns needs both series PMOS and is the slow, load-dependent edge.",
         "With 30 fF the rise takes about 320 ps instead of about 23 ps: the same RC argument as before, now with R of two series PMOS."])
S += qa([("Why are the NOR PMOS transistors four times wider?", "Two PMOS in series double the resistance, and a PMOS is already about 2x weaker than an NMOS. Making each PMOS 4x the NMOS width restores a rise time equal to the fall time."),
         ("NAND or NOR: which is faster for the same area?", "NAND, because its series path is made of NMOS."),
         ("What does the pull-up/pull-down duality mean?", "Where the pull-down has transistors in series, the pull-up has them in parallel and vice versa, so exactly one network conducts for every input.")])
S += [PageBreak()]

# ---- half adder
S += [p("1.7 Half Adder", H1)]
S += [side(img(exp_img("06", "exp6_halfadder_sch.png"), 8.6 * cm, "Half adder: Sum = A xor B from four NAND gates, Carry = A.B from a NAND and an inverter."),
           [table([["A B", "Sum", "Carry"], ["0 0", "0", "0"], ["0 1", "1", "0"], ["1 0", "1", "0"], ["1 1", "0", "1"]], [1.6 * cm, 2.2 * cm, 2.2 * cm]),
            Spacer(1, 4)] + bl(["<b>Sum</b> = A xor B. With NAND gates: n1 = (AB)', n2 = (A n1)', n3 = (B n1)', Sum = (n2 n3)'. Three gate levels.",
                                 "<b>Carry</b> = A.B = ((AB)')', a NAND followed by an inverter.",
                                 "Total: 5 NAND (20 transistors) + 1 inverter (2) = <b>22 transistors</b>. Sum has the longest path (three NAND delays)."]))]
S += [p("Waveform: how to explain it", H2)]
S += [pair(img(exp_img("06", "wave_halfadder_nocap.png"), 8.6 * cm, "Without capacitance"), img(exp_img("06", "wave_halfadder_cap.png"), 8.6 * cm, "With 30 fF capacitance"))]
S += bl(["Inputs a and b step through 00, 01, 10, 11 for 2 ns each. <b>Sum</b> is high for 01 and 10 only; <b>carry</b> is high only for 11.",
         "The sum output toggles a little later than the carry because it passes through three NAND stages.",
         "With the load capacitor both outputs still reach the right logic value, but each edge is about ten times slower."])
S += qa([("Why build XOR from NAND gates?", "To show that NAND is universal and to use one standard cell. A dedicated XOR gate would need more transistors in a single complex cell (about 12 for a static CMOS XOR)."),
         ("How do you get a full adder from this?", "Two half adders and an OR gate: the first adds A and B, the second adds the carry-in; the two carries are ORed."),
         ("Which output limits the speed?", "Sum, because of the three-stage path A to n1 to n2 to Sum.")])
S += [PageBreak()]

# ------------------------------------------------------------------ 2. MUX
S += [p("2. 2:1 Multiplexer and Its Layout", H1),
      p("Function: <b>Y = S'.D0 + S.D1</b>. S = 0 passes D0, S = 1 passes D1."),
      pair(img(exp_img("07", "exp7_mux_gates_sch.png"), 8.4 * cm, "Version 1: logic gates, 1 inverter + 3 NAND = 14 transistors."),
           img(GD + "gate_mux.png", 8.4 * cm, "Version 2: two transmission gates (+ an inverter for S') = 6 transistors."))]
S += [table([["", "Logic-gate MUX", "Transmission-gate MUX"],
             ["Transistors", "14", "6 (2 TG + inverter)"],
             ["How it works", "S selects one NAND to be transparent; the last NAND combines the two", "S turns on exactly one TG; the selected input connects straight to Y"],
             ["Output", "Restored to a full level by the last NAND", "Not restored: Y is driven through the TG on-resistance"],
             ["Voltage levels", "Full 0 and full 1", "TG passes both 0 and 1 fully: NMOS passes a good 0, PMOS a good 1, together no threshold loss"],
             ["Speed (our simulation)", "rise 35 ps, fall 24 ps; with 30 fF: 333 / 324 ps", "rise 31 ps, fall 31 ps; with 30 fF: 291 / 291 ps"],
             ["Weak point", "More area and delay", "Needs S and S' (complementary), no gain, speed depends on the driving source"]],
            [3 * cm, 7 * cm, 7.4 * cm]),
      p("2.1 Waveform: how to explain it", H2)]
S += [pair(img(exp_img("07", "wave_mux_tg_nocap.png"), 8.6 * cm, "Transmission-gate MUX, no capacitance"), img(exp_img("07", "wave_mux_tg_cap.png"), 8.6 * cm, "Transmission-gate MUX, 30 fF"))]
S += bl(["Traces: select <b>s</b>, data <b>d1</b>, <b>d0</b> (green) and the output <b>y</b> (red). The eight input combinations of (s, d1, d0) run in turn, 1.5 ns each.",
         "While s = 0 (first half) y copies <b>d0</b> and ignores d1. After s rises (6 ns) y copies <b>d1</b> and ignores d0.",
         "With the 30 fF load the output follows with slow RC edges, because it is driven through the transmission gate resistance."])
S += [PageBreak()]

S += [p("2.2 How to draw the layout of the 2:1 MUX (Microwind)", H1)]
S += [side(img(exp_img("07", "microwind_mux.png"), 9.2 * cm, "MUX.MSK in Microwind: N-well on top, PMOS diffusion (olive), NMOS diffusion (green), poly (red), metal 1 (blue), contacts."),
           [p("<b>Layer colours in Microwind</b>", SM),
            table([["Layer", "Colour", "Used for"], ["N-well", "dark green dotted box", "holds the PMOS"], ["P+ diffusion", "olive", "PMOS source/drain"],
                   ["N+ diffusion", "green", "NMOS source/drain"], ["Polysilicon", "red", "gates; a transistor appears where poly crosses diffusion"],
                   ["Contact", "box with an X", "joins metal to poly or diffusion"], ["Metal 1", "blue", "wires, VDD and VSS rails"]], [2.2 * cm, 3 * cm, 3.4 * cm]),
            Spacer(1, 3),
            p("<b>Design rules (cmos012, lambda = 0.06 um):</b> poly width 2 lambda, poly sticks out 2 lambda past the diffusion, contact 2 x 2 lambda, metal 1 width 4 lambda, "
              "N-well larger than the PMOS diffusion by at least 3 lambda.", SM)], wl=9.4 * cm, wr=8.4 * cm)]
S += [p("Steps", H2)]
S += bl(["<b>1. Set up.</b> Start Microwind, File &gt; Select Foundry &gt; <i>cmos012.rul</i>. The grid dots are 5 lambda apart.",
         "<b>2. N-well and PMOS.</b> Draw a rectangle on the N-well layer for the PMOS side. Inside it draw a strip of P+ diffusion (the PMOS channel row).",
         "<b>3. NMOS.</b> Below, outside the well, draw a strip of N+ diffusion (the NMOS row).",
         "<b>4. Poly gates.</b> Draw vertical poly lines across the strips. <b>Important for a transmission gate:</b> the NMOS and the PMOS of one TG need <i>opposite</i> gate signals (S and S'), "
         "so one poly line cannot run through both strips. Draw separate poly pieces and join each to its signal with metal 1.",
         "<b>5. Contacts.</b> Put 2 x 2 lambda contacts on every source/drain and on the poly ends that connect to metal.",
         "<b>6. Metal 1.</b> VDD rail above the well (with an N+ tap into the well), VSS rail below (with a P+ tap into the substrate). Connect D0 and D1 to the outer diffusion nodes and join the two TG output nodes into <b>Y</b>.",
         "<b>7. Inverter for S'.</b> Add a small PMOS + NMOS pair sharing one poly gate (input S, output S') next to the TGs.",
         "<b>8. Names and sources.</b> Add text labels D0, D1, S, Y, Vdd, Vss. Mark Vdd with the supply tool and attach clocks to S, D0 and D1 with the Add-clock tool.",
         "<b>9. Check and simulate.</b> Analysis &gt; Design Rule Checker, then Simulate &gt; Start Simulation, tab Voltage vs time. Y must follow D0 when S = 0 and D1 when S = 1.",
         "<b>Shortcut for the logic-gate version:</b> draw the schematic in DSCH, File &gt; Make Verilog File, then in Microwind Compile &gt; Compile Verilog File. The compiler places and routes the gates for you (<i>MUX.TXT</i> in this repository)."])
S += qa([("Why is the layout of the TG MUX smaller than the gate MUX?", "It has 6 transistors instead of 14, and no extra wiring between NAND stages."),
         ("Why does a transmission gate need both an NMOS and a PMOS?", "An NMOS alone passes a weak 1 (output stops at VDD - Vt); a PMOS alone passes a weak 0. In parallel they pass the full range."),
         ("What is the N-well for?", "The PMOS needs an n-type body. The N-well is an n-type island in the p-type substrate and is tied to VDD; the NMOS body is the substrate tied to VSS."),
         ("What does DRC check?", "Minimum widths, spacings and overlaps of the layers against the process rules (here lambda = 0.06 um).")])
S += [PageBreak()]

# ------------------------------------------------------------------ 3. SRAM, DFF
S += [p("3. 6T SRAM Cell", H1)]
S += [side(img(GD + "gate_sram.png", 8.6 * cm, "6T SRAM: two cross-coupled inverters (4 transistors) and two NMOS access transistors controlled by the word line WL."),
           bl(["<b>Hold</b> (WL = 0): the access transistors are OFF; the two inverters feed each other and keep Q and Q' stable (positive feedback, a bistable circuit).",
               "<b>Write</b> (WL = 1): the bit lines are driven to the new value (BL = 1, BL' = 0 writes a 1). The access transistor must be <b>stronger than the pull-up PMOS</b> to overpower it.",
               "<b>Read</b> (WL = 1): both bit lines are first <b>precharged</b> to VDD and left floating. The side that stores 0 discharges its bit line through the access and pull-down transistors; the small difference is sensed.",
               "<b>Sizing in our simulation:</b> pull-up W/L 1, pull-down 3, access 2. The pull-down must beat the access transistor (cell ratio 3/2 = 1.5) so a read does not flip the stored 0."]), wl=8.8 * cm, wr=8.8 * cm)]
S += [p("Waveform: how to explain it", H2),
      pair(img(exp_img("08", "wave_sram_nocap.png"), 8.6 * cm, "Without bit-line capacitance"), img(exp_img("08", "wave_sram_cap.png"), 8.6 * cm, "With 30 fF on each bit line"))]
S += bl(["Traces from top: word line <b>wl</b>, bit lines <b>bl</b> and <b>blb</b>, and the stored nodes <b>q</b> and <b>qb</b>.",
         "<b>1 to 3 ns, write 1:</b> wl high, bl = 1, blb = 0. q rises to 1, qb falls to 0 (37 ps). <b>3 to 5 ns, hold:</b> wl low; q stays at 1 even when the bit lines change.",
         "<b>4 to 5 ns:</b> both bit lines precharged to VDD. <b>5 to 6 ns, read:</b> wl high, bit lines floating; blb falls because qb = 0, bl stays high. q is not disturbed.",
         "<b>6.5 to 8 ns, write 0:</b> bl = 0, blb = 1 flips the cell: q falls to 0 (15 ps).",
         "<b>With 30 fF on the bit lines</b> writing is unchanged (the bit lines are driven hard) but the read discharge is slow: wl to blb at 50 % takes 133 ps instead of 15 ps."])
S += qa([("Why six transistors?", "Four make the bistable latch and two let you reach it. It stores a bit as long as power is applied, with no refresh, which is why it is used for cache memory."),
         ("SRAM vs DRAM?", "SRAM: 6T, fast, no refresh, bigger. DRAM: 1 transistor + 1 capacitor, dense and cheap, but the charge leaks, so it must be refreshed."),
         ("Why precharge the bit lines?", "So both start at the same level and the tiny difference caused by the cell can be sensed quickly by a sense amplifier.")])
S += [PageBreak(),
      p("3.1 CMOS D Flip-Flop", H1)]
S += [side(img(exp_img("10", "microwind_dff.png"), 9.0 * cm, "DFF.MSK in Microwind."),
           bl(["A D flip-flop copies D to Q only on the <b>active clock edge</b> and holds it until the next edge.",
               "<b>Master-slave:</b> two D latches in series, enabled by opposite clock phases. While clk = 0 the master follows D and the slave holds; at the rising edge the master freezes and the slave passes its value to Q. The output therefore changes once per clock.",
               "A <b>latch</b> is level-sensitive (transparent while enabled); a <b>flip-flop</b> is edge-triggered. Mention setup time (D stable before the edge), hold time (after) and clock-to-Q delay.",
               "In this repository <i>DFF.TXT</i> describes a flip-flop with six NAND gates that Microwind can compile into a layout."]), wl=9.2 * cm, wr=8.4 * cm)]
S += qa([("Why does the master-slave structure avoid the race-through problem?", "Only one latch is transparent at a time, so D can never ripple through both in one clock phase."),
         ("What is metastability?", "If D changes right at the clock edge (violating setup or hold) the flip-flop can sit between 0 and 1 for a while before settling; synchronizer flip-flops are used to make that harmless.")])
S += [PageBreak()]

# ------------------------------------------------------------------ 4. FPGA / CPLD
S += [p("4. FPGA vs CPLD", H1),
      p("Both are <b>programmable logic devices</b>: you describe a circuit in VHDL or Verilog and a tool turns it into a configuration. The difference is how the logic and wiring are built."),
      table([["", "CPLD", "FPGA"],
             ["Building block", "Large PAL-like blocks: an AND-OR array (sum of products) feeding macrocells with a flip-flop", "Many small cells (CLB/slice) each with look-up tables (LUT) and flip-flops"],
             ["Granularity", "Coarse", "Fine"],
             ["Interconnect", "One central switch matrix; same delay for every path", "Programmable routing channels; delay depends on placement and routing"],
             ["Configuration memory", "EEPROM / flash: non-volatile, ready at power-on", "SRAM: volatile, loaded from a flash chip at every power-up (a few flash-based FPGAs exist)"],
             ["Capacity", "Hundreds to a few thousand macrocells", "Thousands to millions of LUTs, plus block RAM, DSP slices, clock managers, transceivers"],
             ["Timing", "Predictable pin-to-pin delay", "Must be checked with static timing analysis after place and route"],
             ["Power and cost", "Low power, low cost for small designs", "Higher power; cost grows with size"],
             ["Typical use", "Glue logic, address decoding, small state machines, boot control", "DSP, image processing, soft CPUs, ASIC prototyping, parallel computing"],
             ["In our lab", "-", "Boolean Board: Xilinx Spartan-7 FPGA, programmed from Vivado over USB"]],
            [3.2 * cm, 7 * cm, 7.2 * cm]),
      p("4.1 What is a LUT?", H2),
      p("A k-input LUT is a tiny memory with 2<super>k</super> bits that stores the truth table of any function of k inputs. The inputs are the address; the stored bit is the output. "
        "Spartan-7 uses 6-input LUTs (64 stored bits), so any function of up to six inputs fits in one LUT. Larger functions are split across several LUTs connected by the routing."),
      p("4.2 FPGA design flow (what you did in Vivado)", H2)]
S += bl(["<b>Design entry:</b> write the VHDL (design file plus a testbench).",
         "<b>Behavioural simulation:</b> run the testbench and check the waveform. No hardware yet.",
         "<b>Synthesis:</b> the tool converts the VHDL into gates and flip-flops, then maps them to LUTs (the elaborated schematic shows the result).",
         "<b>Implementation:</b> place the cells on the chip and route the wires; check timing.",
         "<b>Constraints (XDC):</b> tell the tool which FPGA pin goes to which switch, LED or button.",
         "<b>Bitstream and programming:</b> generate the .bit file and download it with the Hardware Manager; the design runs on the board."])
S += qa([("Why use an FPGA and not a microcontroller?", "A microcontroller runs instructions one after another. An FPGA builds real hardware, so many operations run in parallel and with deterministic timing."),
         ("FPGA vs ASIC?", "An ASIC is custom silicon: fastest and cheapest per chip at volume, but very expensive to design and cannot be changed. An FPGA is reprogrammable and has no upfront mask cost."),
         ("Why does an SRAM-based FPGA need a configuration chip?", "SRAM loses its contents without power, so the bitstream must be reloaded from non-volatile memory each time the board is powered."),
         ("Why is a CPLD faster to start?", "Its configuration is stored on-chip in non-volatile memory, so it works the instant power is applied.")])
S += [PageBreak()]


# ------------------------------------------------------------------ 5. VHDL experiments
def vhdl_page(num, title, what, design, wave_img, wave_cap, wave_pts, questions):
    out = [p("5.%s %s" % (num, title), H1), p("<b>What it does.</b> " + what), p("How the code is built, and why", H2)] + bl(design)
    out += [p("Waveform: how to explain it", H2)] + img(wave_img, W17, wave_cap) + bl(wave_pts) + [p("Viva questions", H2)] + qa(questions)
    return out + [PageBreak()]


S += vhdl_page("1", "EXP 1: 4-bit ALU",
    "A combinational circuit with two 4-bit inputs A and B and a 3-bit select SEL. The output Y is one of eight operations.",
    ["<b>Ports:</b> <i>a, b</i> (4-bit in), <i>sel</i> (3-bit in), <i>y</i> (4-bit out). There is <b>no clock</b>, so the circuit is purely combinational.",
     "<b>process(a, b, sel)</b>: the sensitivity list holds every input, so the output is recomputed whenever any of them changes. That is what makes it combinational.",
     "<b>case sel</b> selects one branch: 000 A+B, 001 A-B, 010 A and B, 011 A nand B, 100 A xor B, 101 A xnor B, 110 A or B, and <b>when others</b> (111) passes A. "
     "<i>others</i> is required because a 3-bit std_logic_vector can hold values like U or X; it also guarantees that y is assigned in every case, so no latch is created.",
     "<b>unsigned():</b> std_logic_vector has no + or - operators. numeric_std's <i>unsigned</i> type adds them; the result is cast back with std_logic_vector(). The result is 4 bits wide, so carry or borrow is dropped (wrap-around modulo 16).",
     "<b>In the FPGA:</b> only look-up tables are used (no flip-flops). The case statement becomes an 8-way multiplexer behind the adder/subtractor and the logic gates."],
    VI + "exp1_alu_faculty.png", "Simulation of the faculty ALU code: A = 1100 (12), B = 0011 (3), SEL steps through 000 to 111 every 100 ns.",
    ["A and B stay fixed at 12 and 3. SEL changes every 100 ns, so each step shows one operation.",
     "<b>000 ADD:</b> 12 + 3 = 15 = 1111. <b>001 SUB:</b> 12 - 3 = 9 = 1001. <b>010 AND:</b> 1100 and 0011 = 0000.",
     "<b>011 NAND:</b> not(0000) = 1111. <b>100 XOR:</b> the bits of A and B are complementary, so xor = 1111. <b>101 XNOR:</b> 0000. <b>110 OR:</b> 1111. <b>111:</b> passes A = 1100.",
     "Y changes right after SEL (no clock edge is needed): that is how you show that the ALU is combinational."],
    [("Is the ALU combinational or sequential?", "Combinational: no clock and no memory. The output depends only on the present inputs."),
     ("Why case and not if-elsif?", "A case picks exactly one branch in parallel (a multiplexer). An if-elsif chain creates priority logic that is deeper and slower."),
     ("What happens if A + B does not fit in 4 bits?", "It wraps modulo 16, for example 12 + 5 gives 1. To detect it, compute in 5 bits (resize) and use the extra bit as carry-out."),
     ("Why numeric_std and not std_logic_unsigned?", "numeric_std is the IEEE standard library; std_logic_unsigned is a vendor library that is not part of the standard."),
     ("What does 3 - 12 give?", "In 4-bit unsigned arithmetic, 3 - 12 = -9 which wraps to 7 (0111).")])

S += vhdl_page("2", "EXP 2: Universal Shift Register",
    "A 4-bit register with an asynchronous reset and four modes: hold, parallel load, shift left and shift right. 'Universal' means it can do all of these.",
    ["<b>Ports:</b> <i>clk</i>, <i>rst</i> (asynchronous reset), <i>mode</i> (2 bits), <i>i</i> (parallel input), <i>il</i> (serial input for right shift), <i>ir</i> (serial input for left shift), <i>q</i> (output).",
     "<b>process(clk, rst)</b>: <i>rst</i> is in the sensitivity list and is tested <b>before</b> rising_edge(clk), so the reset is <b>asynchronous</b>: it clears the register at once, without waiting for a clock edge.",
     "<b>case mode</b> (only on the rising edge): <b>00</b> hold (qtmp &lt;= qtmp), <b>01</b> parallel load (qtmp &lt;= i), <b>10</b> shift left (qtmp(2 downto 0) &amp; ir: the new bit <i>ir</i> enters at the LSB), "
     "<b>11</b> shift right (il &amp; qtmp(3 downto 1): the new bit <i>il</i> enters at the MSB).",
     "<b>Internal signal qtmp:</b> an output port cannot be read inside the architecture in VHDL-93, so the register value lives in <i>qtmp</i> and <i>q &lt;= qtmp</i> drives the port.",
     "<b>In the FPGA:</b> four flip-flops, each with a 4-way multiplexer on its D input made of one LUT. 'Hold' is just a flip-flop with a clock enable.",
     "The file <i>shiftregister.vhd</i> is only the testbench: it has no ports, makes a 100 ns clock and applies the stimulus."],
    VI + "exp2_shiftreg_faculty.png", "Simulation of the faculty shift register code.",
    ["<b>0 to 100 ns:</b> rst = 1, so Q = 0000. <b>150 ns, mode 01:</b> Q loads I = 1010.",
     "<b>mode 00:</b> Q holds 1010. <b>350 ns, mode 10 with IR = 1:</b> left shift: Q = 0101 (the 1 entered at the right). <b>450 ns</b> (IR = 0): Q = 1010.",
     "<b>550 ns, mode 11 with IL = 1:</b> right shift: Q = 1101 (the 1 entered at the left). <b>650 ns</b> (IL = 0): Q = 0110.",
     "<b>750 ns:</b> load 1100, then hold. <b>900 ns:</b> rst = 1 clears Q to 0000 immediately, in the middle of a clock period: this is how you show that the reset is asynchronous."],
    [("What is a universal shift register?", "One that supports serial-in, serial-out, parallel-in and parallel-out, with shifts in both directions and hold. Also called SISO, SIPO, PISO and PIPO in one device."),
     ("Asynchronous vs synchronous reset?", "Asynchronous: acts as soon as rst is 1 (listed in the sensitivity list). Synchronous: acts only at the next clock edge. Asynchronous is quicker but must be released cleanly."),
     ("What does shifting left do numerically?", "Shifting left by one with 0 entering doubles the value (1010 becomes 0100 plus the carried bit)."),
     ("How would you make a PISO converter?", "Load the word in parallel, then shift every clock and read the serial bit from one end."),
     ("Why is there no latch for the hold mode?", "The assignment is inside a clocked process, so it is just a flip-flop that keeps its value.")])

S += vhdl_page("3", "EXP 3: 4-bit Counter",
    "A 4-bit binary counter with an asynchronous clear. It counts 0 to 15 and wraps to 0. (The lab file <i>bitcounter.vhd</i> counts up only; the same idea gives an up-down counter by adding a direction input.)",
    ["<b>Ports:</b> <i>clk</i>, <i>clr</i> (asynchronous clear), <i>q</i> (4-bit output). <b>Internal signal tmp</b> holds the count so <i>q &lt;= tmp</i> can drive the port.",
     "<b>process(clk, clr)</b>: if clr = '1' the count is forced to 0000 at once; otherwise on every rising edge <b>tmp &lt;= tmp + 1</b>.",
     "<b>Wrap-around:</b> unsigned 4-bit arithmetic wraps, so 1111 + 1 = 0000 without extra code. The counter has 16 states (modulo 16).",
     "<b>Up-down version:</b> add an input <i>up</i>: <i>if up = '1' then tmp + 1 else tmp - 1</i>, and optionally an enable. <b>Decade counter:</b> clear when tmp = 1001.",
     "<b>In the FPGA:</b> 4 flip-flops and a small incrementer in LUTs. The clock runs on a dedicated clock route."],
    VI + "exp3_counter_faculty.png", "Simulation of the faculty counter code (clock period 20 ns).",
    ["<b>0 to 20 ns:</b> clr = 1, so Q stays 0. clr is released at 20 ns.",
     "<b>30 ns:</b> the first rising edge after clr = 0: Q = 1. From then on Q increases by 1 every 20 ns (every clock): 2 at 50 ns, 3 at 70 ns, and so on.",
     "<b>310 ns:</b> Q = 15 (1111). <b>330 ns:</b> the next edge wraps Q to 0 and counting continues (1 at 350 ns, 2 at 370 ns).",
     "Frequency division: Q0 toggles at half the clock frequency, Q1 at a quarter, Q2 at an eighth and Q3 at a sixteenth. So the counter is also a divide-by-2, 4, 8, 16 chain."],
    [("What is the modulus of this counter?", "16 (it has 2<super>4</super> states)."),
     ("Synchronous or asynchronous counter?", "Synchronous: all flip-flops share one clock. A ripple (asynchronous) counter chains the flip-flop outputs as clocks and is slower."),
     ("How do you change it to count down?", "Use tmp - 1 instead of tmp + 1, or choose with an up/down input."),
     ("How do you make a mod-10 counter?", "Compare tmp with 1001 and load 0000 on the next edge (or use clr)."),
     ("Why is the clear in the sensitivity list?", "Because it is asynchronous: the process must wake up when clr changes, not only on the clock.")])

S += vhdl_page("4", "EXP 4: FIFO Memory",
    "A first-in first-out buffer: 4 words of 4 bits. Words come out in the order they went in. It reports <i>full</i> and <i>empty</i>.",
    ["<b>Storage:</b> <i>memory_type</i> is an array of 4 words, each 4 bits. <b>Pointers:</b> <i>writeptr</i> and <i>readptr</i> (2 bits) point at the next word to write and read; they wrap from 3 to 0, so the memory works as a <b>circular buffer</b>.",
     "<b>count</b> (3 bits, 0 to 4) tells how many words are stored. When the two pointers are equal the FIFO could be completely full <i>or</i> completely empty; using a count removes that ambiguity.",
     "<b>One clocked process.</b> rst = 1 (synchronous) clears the pointers and the count. Otherwise: <i>do_write</i> = enw and count &lt; 4; <i>do_read</i> = enr and count &gt; 0. So a write when full and a read when empty are simply ignored.",
     "A write stores datain at writeptr and increments it. A read puts memory(readptr) on <i>dataout</i> and increments readptr. The count goes up for a write only, down for a read only, and stays the same if both happen together.",
     "<b>Flags:</b> <i>empty = 1 when count = 0</i>, <i>full = 1 when count = 4</i>, both combinational.",
     "<b>dataout is registered</b>, so a word appears on the clock edge after the read request."],
    VI + "exp4_fifo_faculty.png", "Simulation of the faculty FIFO code (clock period 100 ns).",
    ["<b>0 to 100 ns:</b> rst = 1: pointers and count cleared, <i>empty = 1</i>.",
     "<b>200 ns on:</b> enw = 1 and datain = 0001, 0010, 0011, 0100, one per clock. The words are written at 250, 350, 450 and 550 ns. <i>empty</i> falls at 250 ns; <b>full rises at 550 ns</b> (4 words stored).",
     "<b>700 ns on:</b> enr = 1. dataout shows <b>0001 at 750 ns, 0010 at 850, 0011 at 950, 0100 at 1050</b>: first in, first out. <i>full</i> falls at 750 ns and <b><i>empty</i> rises at 1050 ns</b>.",
     "<b>1250 ns:</b> 1010 is written; <b>1350 ns:</b> it is read back and dataout = 1010, empty = 1 again."],
    [("What is a FIFO used for?", "Buffering between two parts that run at different rates or clock domains, for example a UART, a camera or a network interface."),
     ("Why a circular buffer?", "The pointers just wrap around, so no data has to be moved."),
     ("Why use a count?", "With only two pointers, equal pointers mean both full and empty. The count makes the two cases distinct."),
     ("What happens if you write when the FIFO is full?", "do_write is false, so the write is ignored and nothing is overwritten."),
     ("Synchronous vs asynchronous FIFO? How do you make it deeper?", "This one uses one clock for both sides; an asynchronous FIFO has separate read and write clocks and needs Gray-coded pointers. For more depth, enlarge the array and pointer width (large FIFOs map to block RAM).")])

S += vhdl_page("5", "EXP 5: 4x4 Keypad Interface",
    "Reads a 16-key matrix keypad and shows which key is pressed on the 8 LEDs of the Boolean Board.",
    ["<b>Matrix:</b> 16 keys need only 4 + 4 = 8 pins. A key connects its row to its column. The <b>rows (a)</b> are outputs, the <b>columns (b)</b> are inputs with pull-ups, so b = 1111 when nothing is pressed.",
     "<b>Scanning:</b> one row at a time is driven low (0111, 1011, 1101, 1110). If a key in that row is pressed, its column reads 0. The position (row, column) identifies the key.",
     "<b>Timing from one counter:</b> <i>sig1</i> is a 30-bit counter that increments every clock. Its bits (10 downto 8) form a 3-bit state that changes every 256 clocks (2.56 us at 100 MHz). "
     "Even states (000, 010, 100, 110) <b>set the row</b>; the following odd state <b>reads the columns</b>, giving the row a full phase to settle. Each row is active for 5.12 us and a complete scan takes 20.48 us (about 49 kHz).",
     "<b>LED code:</b> the pattern repeats the key value in both nibbles: key 5 gives 01010101, B gives 10111011, 0 gives 00000000, F gives 11111111.",
     "<b>No key pressed:</b> no branch assigns <i>led</i>, so it keeps its last value (a register). <b>Limitations:</b> there is no debounce; a real design waits 10 to 20 ms for the contact to stop bouncing."],
    VI + "exp5_keypad_faculty.png", "Testbench simulation (100 MHz clock): key 5 (row 2, column 1101) is pressed at 0.1 us and released at 25.1 us.",
    ["<b>Row a</b> cycles 0111, 1011, 1101, 1110 and repeats, each value held for 5.12 us.",
     "<b>Column b</b> stays 1111 until the pressed key's row is active: when a = 1011 (row 2) b becomes 1101, the column of key 5.",
     "<b>LED</b> changes to 01010101 at about 7.7 us: the first read phase after row 2 became active. After the key is released LED keeps 01010101 because nothing writes a new value.",
     "The pattern then repeats for every scan, so the keypad is checked about 49 000 times a second."],
    [("Why does a matrix keypad save pins?", "n x m keys need only n + m wires instead of n x m."),
     ("Why are the rows driven low and the columns pulled up?", "An idle column is 1; a pressed key in the low row pulls its column to 0, which is easy to detect."),
     ("Why scan so slowly (256 clocks per phase)?", "To give the row line time to settle before the columns are read. It is still far faster than a human keypress."),
     ("What is switch bounce?", "The contact opens and closes several times for a few milliseconds. Debounce by sampling the same value for 10 to 20 ms."),
     ("What happens if two keys are pressed together?", "Ghosting: two keys in the same row can be confused; this simple design shows whichever it reads last.")])

# ------------------------------------------------------------------ 6. quick answers
S += [p("6. Why Is the Design Like That? One-Line Answers", H1),
      table([["Question", "Answer"],
             ["Why PMOS in the pull-up and NMOS in the pull-down?", "PMOS passes a strong 1 and NMOS a strong 0. The opposite choice would lose a threshold voltage at the output."],
             ["Why PMOS 2x wider than NMOS?", "Holes are about 2-3x slower than electrons; the wider PMOS equalises rise and fall times and puts V<sub>M</sub> near VDD/2."],
             ["Why NAND NMOS = 2 and NOR PMOS = 4?", "Series transistors double the resistance, so each is made 2x wider to match a single inverter transistor."],
             ["Why use a load capacitor in the experiment?", "Real gates drive wires and other gates. It shows how delay (t = RC) and power (CV<super>2</super>f) depend on the load."],
             ["Why a transmission-gate MUX?", "Six transistors instead of fourteen, with full-level outputs, but the output is not restored."],
             ["Why precharge the SRAM bit lines?", "So the stored bit produces a small, fast, detectable difference."],
             ["Why is the SRAM pull-down stronger than the access transistor?", "A read must not flip the stored 0; a write must still win against the pull-up PMOS."],
             ["Why master-slave flip-flop?", "Two opposite-phase latches give one change per clock edge and no race-through."],
             ["Why case in the ALU?", "One parallel multiplexer, no priority chain, and the compiler checks that every case is covered."],
             ["Why an internal signal (qtmp, tmp) in registers and counters?", "An output port cannot be read inside the architecture in VHDL-93; the signal holds the value."],
             ["Why asynchronous clear/reset?", "It clears the register immediately, without needing a clock; the clock is not running at power-up."],
             ["Why a count in the FIFO?", "Equal pointers mean full or empty; the count removes the ambiguity."],
             ["Why scan the keypad?", "8 pins serve 16 keys; one row at a time is driven and the columns are read."],
             ["Why an FPGA?", "Real parallel hardware with reprogrammable logic, no fabrication cost: ideal for labs and prototypes."]],
            [6.2 * cm, 11.2 * cm])]

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        ap = os.path.join(tmp, "viva.pdf")
        SimpleDocTemplate(ap, pagesize=A4, leftMargin=1.7 * cm, rightMargin=1.7 * cm, topMargin=1.5 * cm, bottomMargin=1.4 * cm, title="Viva Explanations").build(S)
        base, viva = pypdf.PdfReader(BASE), pypdf.PdfReader(ap)
        if len(base.pages) < BASE_PAGES: sys.exit("base PDF has %d pages, expected at least %d" % (len(base.pages), BASE_PAGES))
        w = pypdf.PdfWriter()
        for pg in base.pages[:BASE_PAGES]: w.add_page(pg)
        for pg in viva.pages: w.add_page(pg)
        w.add_metadata({"/Title": "VLSI D&T Study Notes"})
        new_vlsi = os.path.join(tmp, "vlsi.pdf"); w.write(new_vlsi)
        c = pypdf.PdfWriter()
        for pg in pypdf.PdfReader(new_vlsi).pages: c.add_page(pg)
        for pg in pypdf.PdfReader(NOTES_DIR + "MIOT Study Notes.pdf").pages: c.add_page(pg)
        c.add_metadata({"/Title": "VLSI and MIOT Study Notes"})
        combined = os.path.join(tmp, "combined.pdf"); c.write(combined)
        for d in (NOTES_DIR, os.path.expanduser("~/Documents/")):
            if os.path.isdir(d):
                shutil.copyfile(new_vlsi, d + "VLSI D&T Study Notes.pdf"); shutil.copyfile(combined, d + "VLSI and MIOT Study Notes.pdf")
        print("viva pages:", len(viva.pages), "| VLSI notes now", len(pypdf.PdfReader(new_vlsi).pages), "pages | combined", len(c.pages))
