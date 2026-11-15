"""Build one single-column .docx per experiment (Exp 1-8) from src/, img/ and sim/results.json."""
import json
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

SRC, IMG, OUT = "../src/", "../img/", "../"
R = json.load(open("../sim/results.json"))

def new_doc(title):
    d = Document()
    s = d.sections[0]
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(2.0)
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
    h = d.add_paragraph(); r = h.add_run(title); r.bold = True; r.font.size = Pt(16)
    return d

def heading(d, text):
    p = d.add_paragraph(); r = p.add_run(text); r.bold = True; r.font.size = Pt(12.5)
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.keep_with_next = True

def para(d, text, italic=False):
    p = d.add_paragraph(); r = p.add_run(text); r.italic = italic; return p

def code(d, path, caption=None):
    heading(d, caption or path.split("/")[-1])
    lines = open(path).read().rstrip().split("\\n") if False else open(path).read().rstrip().split("\n")
    for ln in lines:                                  # one paragraph per line, single column, shaded
        p = d.add_paragraph(); pf = p.paragraph_format
        pf.space_after = pf.space_before = Pt(0); pf.line_spacing = 1.0
        r = p.add_run(ln if ln else " "); r.font.name = "Consolas"; r.font.size = Pt(8.5)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), "F2F2F2")
        p._p.get_or_add_pPr().append(shd)

def image(d, name, caption, width=6.3):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(IMG + name, width=Inches(width))
    p.paragraph_format.keep_with_next = True
    c = d.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(caption); r.italic = True; r.font.size = Pt(9.5)

def table(d, rows, header=True, widths=None):
    t = d.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            cell = t.cell(i, j); cell.text = ""
            r = cell.paragraphs[0].add_run(str(v)); r.font.size = Pt(9.5)
            if header and i == 0: r.bold = True
    if widths:
        for row in t.rows:
            for c, w in zip(row.cells, widths): c.width = Cm(w)
    d.add_paragraph()

def ps(x): return "n/a" if x is None else f"{x * 1e12:.0f} ps"

def out_heading(d, simulated_with):
    heading(d, "Output"); para(d, simulated_with, True)

SIM = "Simulation: VHDL testbench (self-checking)."
PB = "Simulation: transistor-level transient, VDD = 1.2 V, 30 fF load. Rise/fall = 10-90 %."
def bullets(d, items):
    heading(d, "Comments")
    for x in items: d.add_paragraph(x, style="List Bullet")
def pins(d, rows):
    heading(d, "Boolean Board mapping"); table(d, [["Port", "Board resource"]] + rows, widths=[6, 10])

# ===== Exp 1 =====
d = new_doc("VLSI D&T EXP 01")
para(d, "Aim: 4-bit ALU in VHDL (add, subtract, AND, OR, XOR, pass A/B, B-A).")
image(d, "exp1_block.png", "Block diagram", 3.6)
table(d, [["S2 S1 S0", "Operation", "S2 S1 S0", "Operation"], ["000", "A + B", "100", "Pass B"], ["001", "A - B", "101", "A XOR B"],
          ["010", "A AND B", "110", "B - A"], ["011", "A OR B", "111", "Pass A"]])
code(d, SRC + "alu4bit.vhd", "alu4bit.vhd"); code(d, SRC + "alu4bit_tb.vhd", "alu4bit_tb.vhd")
out_heading(d, SIM); image(d, "exp1_wave.png", "Waveform: all 8 functions for A=10, B=3 and A=5, B=12")
pins(d, [["A[3:0]", "SW3..SW0"], ["B[3:0]", "SW7..SW4"], ["S[2:0]", "SW10..SW8"], ["Y[3:0]", "LD3..LD0"]])
d.save(OUT + "VLSI D&T EXP 01.docx")

# ===== Exp 2 =====
d = new_doc("VLSI D&T EXP 02")
para(d, "Aim: Universal shift register with mode select (PIPO, SIPO, PISO, SISO).")
image(d, "exp2_block.png", "Block diagram", 4.0)
table(d, [["S1 S0", "Mode"], ["00", "Parallel load"], ["01", "Shift right (IL in)"], ["10", "Shift left (IR in)"], ["11", "No change"]], widths=[3, 8])
code(d, SRC + "usr.vhd", "usr.vhd"); code(d, SRC + "usr_tb.vhd", "usr_tb.vhd")
out_heading(d, SIM); image(d, "exp2_wave.png", "Waveform: PIPO, SIPO, hold, shift left, PISO, SISO")
pins(d, [["clk", "BTN0 (debounced)"], ["S[1:0]", "SW1, SW0"], ["IL, IR", "SW2, SW3"], ["P[3:0]", "SW7..SW4"], ["Q[3:0]", "LD3..LD0"]])
d.save(OUT + "VLSI D&T EXP 02.docx")

# ===== Exp 3 =====
d = new_doc("VLSI D&T EXP 03")
para(d, "Aim: 4-bit up/down counter with reset and enable. Board clock divider: 100 MHz / 2^26 = 1.49 Hz.")
image(d, "exp3_block.png", "Block diagram", 4.0)
code(d, SRC + "updown_counter.vhd", "updown_counter.vhd"); code(d, SRC + "updown_counter_tb.vhd", "updown_counter_tb.vhd")
code(d, SRC + "counter_top.vhd", "counter_top.vhd (board wrapper)")
out_heading(d, SIM); image(d, "exp3_wave.png", "Waveform: reset, count up, count down, hold, reset")
pins(d, [["clk100", "100 MHz clock"], ["sw(0) rst, sw(1) en, sw(2) up", "SW0, SW1, SW2"], ["led[3:0]", "LD3..LD0"]])
d.save(OUT + "VLSI D&T EXP 03.docx")

# ===== Exp 4 =====
d = new_doc("VLSI D&T EXP 04")
para(d, "Aim: FIFO memory, 8 locations x 8 bits, with full and empty flags.")
image(d, "exp4_block.png", "Block diagram", 4.2)
code(d, SRC + "fifo.vhd", "fifo.vhd"); code(d, SRC + "fifo_tb.vhd", "fifo_tb.vhd")
out_heading(d, SIM); image(d, "exp4_wave.png", "Waveform: fill to full, read back to empty")
pins(d, [["clk", "BTN0 (debounced)"], ["reset, w, r", "BTN3, SW15, SW14"], ["d[7:0]", "SW7..SW0"], ["q[7:0]", "LD7..LD0"], ["empty, full", "LD14, LD15"]])
d.save(OUT + "VLSI D&T EXP 04.docx")

# ===== Exp 5 =====
d = new_doc("VLSI D&T EXP 05")
para(d, "Aim: 4x4 keypad interface. Key n (= 4 x row + column) lights LED n.")
image(d, "exp5_block.png", "Block diagram", 4.0)
code(d, SRC + "keypad.vhd", "keypad.vhd"); code(d, SRC + "keypad_tb.vhd", "keypad_tb.vhd")
out_heading(d, SIM + " SCAN_DIV = 4 in the testbench."); image(d, "exp5_wave.png", "Waveform: key 0, then key 5")
pins(d, [["clk", "100 MHz clock"], ["row[3:0]", "Pmod JA pins 1-4"], ["col[3:0]", "Pmod JA pins 7-10 (pull-up)"], ["led[15:0]", "LD15..LD0"]])
d.save(OUT + "VLSI D&T EXP 05.docx")

# ===== Exp 6 =====
inv, na, no, ha = R["inverter"], R["nand"], R["nor"], R["halfadder"]
d = new_doc("VLSI D&T EXP 06")
para(d, "Aim: CMOS Inverter, NAND, NOR and Half Adder (120 nm, VDD = 1.2 V); simulate with and without load.")
heading(d, "Inverter"); image(d, "exp6_inverter_sch.png", "Symbol", 2.2)
table(d, [["Device", "Type", "D", "G", "S", "W/L"], ["M1", "PMOS", "out", "in", "VDD", "2"], ["M2", "NMOS", "out", "in", "GND", "1"]])
image(d, "exp6_inverter.png", "Inverter transient", 5.6)
heading(d, "NAND"); image(d, "exp6_nand_sch.png", "Symbol", 2.2)
table(d, [["Device", "Type", "D", "G", "S", "W/L"], ["M1", "PMOS", "out", "A", "VDD", "2"], ["M2", "PMOS", "out", "B", "VDD", "2"],
          ["M3", "NMOS", "out", "A", "x", "2"], ["M4", "NMOS", "x", "B", "GND", "2"]])
image(d, "exp6_nand.png", "NAND transient", 5.6)
heading(d, "NOR"); image(d, "exp6_nor_sch.png", "Symbol", 2.2)
table(d, [["Device", "Type", "D", "G", "S", "W/L"], ["M1", "PMOS", "x", "A", "VDD", "4"], ["M2", "PMOS", "out", "B", "x", "4"],
          ["M3", "NMOS", "out", "A", "GND", "1"], ["M4", "NMOS", "out", "B", "GND", "1"]])
image(d, "exp6_nor.png", "NOR transient", 5.6)
heading(d, "Half adder"); image(d, "exp6_halfadder_sch.png", "Half adder (5 NAND + 1 inverter)", 3.2)
image(d, "exp6_halfadder.png", "Half adder transient", 5.6)
out_heading(d, PB)
table(d, [["Edge", "No load", "30 fF load"],
          ["Inverter rise", ps(inv["without load"]["tr"]), ps(inv["with load"]["tr"])], ["Inverter fall", ps(inv["without load"]["tf"]), ps(inv["with load"]["tf"])],
          ["NAND rise", ps(na["without load"]["tr"]), ps(na["with load"]["tr"])], ["NAND fall", ps(na["without load"]["tf"]), ps(na["with load"]["tf"])],
          ["NOR rise", ps(no["without load"]["tr"]), ps(no["with load"]["tr"])], ["NOR fall", ps(no["without load"]["tf"]), ps(no["with load"]["tf"])],
          ["Sum rise", ps(ha["without load"]["sum_tr"]), ps(ha["with load"]["sum_tr"])], ["Sum fall", ps(ha["without load"]["sum_tf"]), ps(ha["with load"]["sum_tf"])],
          ["Carry rise", ps(ha["without load"]["carry_tr"]), ps(ha["with load"]["carry_tr"])]], widths=[6, 5, 5])
bullets(d, ["The 30 fF load slows every edge about 10x (t ~ 2.2 RC).",
            "Inverter and NOR have equal rise and fall (PMOS sized 2x/4x); NAND falls slowest through its two series NMOS."])
d.save(OUT + "VLSI D&T EXP 06.docx")

# ===== Exp 7 =====
g, t = R["mux_gates"], R["mux_tg"]
d = new_doc("VLSI D&T EXP 07")
para(d, "Aim: CMOS 2:1 multiplexer using logic gates and transmission gates. Y = S.D1 + S'.D0.")
heading(d, "Using logic gates (1 inverter + 3 NAND, 14 transistors)")
image(d, "exp7_mux_gates_sch.png", "Logic-gate MUX", 4.2); image(d, "exp7_mux_gates.png", "Transient", 5.6)
heading(d, "Using transmission gates (6 transistors)")
table(d, [["Device", "Type", "Terminals", "Gate", "W/L"], ["TG1", "NMOS", "D0 - Y", "S'", "1"], ["TG1", "PMOS", "D0 - Y", "S", "2"],
          ["TG2", "NMOS", "D1 - Y", "S", "1"], ["TG2", "PMOS", "D1 - Y", "S'", "2"], ["INV", "N + P", "S to S'", "S", "1 / 2"]])
image(d, "exp7_mux_tg.png", "Transient", 5.6)
out_heading(d, PB)
table(d, [["Edge", "No load", "30 fF load"],
          ["Gate MUX rise", ps(g["without load"]["tr"]), ps(g["with load"]["tr"])], ["Gate MUX fall", ps(g["without load"]["tf"]), ps(g["with load"]["tf"])],
          ["TG MUX rise", ps(t["without load"]["tr"]), ps(t["with load"]["tr"])], ["TG MUX fall", ps(t["without load"]["tf"]), ps(t["with load"]["tf"])]], widths=[6, 5, 5])
bullets(d, ["TG MUX needs 6 transistors vs 14 and passes full 0 and 1 levels.",
            "The load slows both versions about 10x; the unbuffered TG output is driven through its ON resistance."])
d.save(OUT + "VLSI D&T EXP 07.docx")

# ===== Exp 8 =====
s = R["sram"]
d = new_doc("VLSI D&T EXP 08")
para(d, "Aim: Single-bit 6T SRAM cell: write, hold and read, with and without bit-line load.")
table(d, [["Device", "Type", "D", "G", "S", "Role", "W/L"],
          ["M1", "PMOS", "q", "qb", "VDD", "pull-up", "1"], ["M2", "NMOS", "q", "qb", "GND", "pull-down", "3"],
          ["M3", "PMOS", "qb", "q", "VDD", "pull-up", "1"], ["M4", "NMOS", "qb", "q", "GND", "pull-down", "3"],
          ["M5", "NMOS", "bl", "wl", "q", "access", "2"], ["M6", "NMOS", "blb", "wl", "qb", "access", "2"]])
image(d, "exp8_sram.png", "Write 1 (1-3 ns), read (5-6 ns), write 0 (6.5-8 ns)", 6.0)
out_heading(d, PB)
table(d, [["Measurement", "No load", "30 fF bit line"],
          ["Q rise (write 1)", ps(s["without load"]["write1_q_rise"]), ps(s["with load"]["write1_q_rise"])],
          ["Q fall (write 0)", ps(s["without load"]["write0_q_fall"]), ps(s["with load"]["write0_q_fall"])],
          ["Read: wl to blb at 50 %", ps(s["without load"]["read_blb_delay"]), ps(s["with load"]["read_blb_delay"])]], widths=[6, 5, 5])
bullets(d, ["Write is load-independent (bit lines are driven); read is about 9x slower with the loaded bit line.",
            "The stored bit survives the read because the pull-down (W/L 3) beats the access transistor (W/L 2)."])
d.save(OUT + "VLSI D&T EXP 08.docx")
print("built 8 docs")
