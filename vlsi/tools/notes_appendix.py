import sys, io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.utils import ImageReader
import pypdf
GD, SRC, OUT = sys.argv[1:4]
H1 = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=15, leading=19, spaceAfter=4)
CAP = ParagraphStyle("c", fontName="Helvetica", fontSize=8.8, leading=11, alignment=1, textColor=colors.HexColor("#333333"))
NOTE = ParagraphStyle("n", fontName="Helvetica", fontSize=9.5, leading=13, spaceAfter=4)
def img(name, w):
    p = "%s/%s.png" % (GD, name); iw, ih = ImageReader(p).getSize()
    return Image(p, width=w, height=w * ih / iw)
def cell(name, cap, w=8.2 * cm):
    return [img(name, w), Paragraph(cap, CAP)]
def grid(rows):
    t = Table(rows, colWidths=[8.8 * cm, 8.8 * cm]); t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6)]))
    return t
fl = [Paragraph("Gate-level CMOS Diagrams", H1),
      Paragraph("Every CMOS gate has a PMOS pull-up network to VDD and an NMOS pull-down network to GND. PMOS conduct when the input is 0, NMOS when it is 1. Series = AND-like, parallel = OR-like; the pull-up is the dual of the pull-down.", NOTE),
      grid([[cell("gate_not", "<b>NOT</b>: Y = A'. 2 transistors."), cell("gate_nand", "<b>NAND</b>: Y = (AB)'. PMOS parallel, NMOS series. 4T.")],
            [cell("gate_nor", "<b>NOR</b>: Y = (A+B)'. PMOS series, NMOS parallel. 4T."), cell("gate_xor", "<b>XOR</b>: Y = A'B + AB'. Needs A', B' from two inverters.")]]),
      PageBreak(),
      Paragraph("Compound Gates, Transmission Gate, MUX and SRAM", H1),
      grid([[cell("gate_and", "<b>AND</b> = NAND + inverter (6T). Non-inverting gates need an extra stage.", 8.6 * cm), cell("gate_or", "<b>OR</b> = NOR + inverter (6T).", 8.6 * cm)],
            [cell("gate_xnor", "<b>XNOR</b>: Y = AB + A'B'. Same as XOR with the A/B' branches swapped."), cell("gate_tg", "<b>Transmission gate</b>: NMOS + PMOS in parallel passes both 0 and 1 without threshold loss.")],
            [cell("gate_mux", "<b>2:1 MUX</b> from two transmission gates: S=0 passes A, S=1 passes B."), cell("gate_sram", "<b>6T SRAM</b>: two cross-coupled inverters hold the bit, two NMOS access transistors (WL) connect to BL, BL'.")]]),
      PageBreak(),
      Paragraph("Stick Diagrams", H1),
      Paragraph("A stick diagram is a symbolic layout: lines for layers, no sizes. Colours: <font color='#2eaa3c'><b>green</b></font> n-diffusion, <font color='#e8a317'><b>orange</b></font> p-diffusion, <font color='#d62828'><b>red</b></font> polysilicon, <font color='#2f5be7'><b>blue</b></font> metal, black squares are contacts. A transistor forms wherever poly crosses diffusion. Rules: VDD rail on top, GND rail at the bottom, PMOS above NMOS, poly runs vertically.", NOTE),
      grid([[cell("stick_not", "<b>Inverter</b>: one poly crosses both strips."), cell("stick_nand", "<b>NAND</b>: PMOS share VDD at the ends (parallel), NMOS chain to GND (series).")],
            [cell("stick_nor", "<b>NOR</b>: PMOS chain from VDD (series), NMOS both to GND (parallel)."), ""]]),
      Paragraph("<b>Steps to draw one:</b> 1) draw VDD and GND rails. 2) draw the p-diffusion and n-diffusion strips. 3) cross them with poly lines, one per input. 4) place contacts and join with metal for the output. 5) check series/parallel matches the logic.", NOTE)]
SimpleDocTemplate(OUT, pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm, topMargin=1.6 * cm, bottomMargin=1.4 * cm, title="Gate and Stick Diagrams").build(fl)
r = pypdf.PdfReader(SRC); a = pypdf.PdfReader(OUT); w = pypdf.PdfWriter()
for i, p in enumerate(r.pages):
    w.add_page(p)
    if i == 13:
        for q in a.pages: w.add_page(q)
w.write(sys.argv[4]); print(len(r.pages), "+", len(a.pages))
