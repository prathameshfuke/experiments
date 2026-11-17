"""Build the gate + stick diagram pages and insert them after the VLSI section (page 14) of the study notes.
Usage: python3 notes_appendix.py <diagram_dir> <notes_in.pdf> <appendix_out.pdf> <notes_out.pdf>"""
import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table, TableStyle, PageBreak
from reportlab.lib.utils import ImageReader
import pypdf
GD, SRC, OUT, FINAL = sys.argv[1:5]
H1 = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=15, leading=19, spaceAfter=4)
CAP = ParagraphStyle("c", fontName="Helvetica", fontSize=8.8, leading=11, alignment=1, textColor=colors.HexColor("#333333"))
NOTE = ParagraphStyle("n", fontName="Helvetica", fontSize=9.5, leading=13, spaceAfter=4)


def fit(name, wmax=13.4 * cm, hmax=6.9 * cm):
    from PIL import Image as PI, ImageChops
    import io
    im = PI.open("%s/%s.png" % (GD, name)).convert("RGB")
    bb = ImageChops.difference(im, PI.new("RGB", im.size, "white")).getbbox()
    if bb: im = im.crop((max(bb[0] - 12, 0), max(bb[1] - 12, 0), min(bb[2] + 12, im.width), min(bb[3] + 12, im.height)))
    buf = io.BytesIO(); im.save(buf, "PNG"); buf.seek(0)
    k = min(wmax / im.width, hmax / im.height)
    return Image(buf, width=im.width * k, height=im.height * k)


ROWS = [("NOT (inverter): Y = A'", "not", "not"), ("NAND: Y = (AB)'", "nand", "nand"), ("NOR: Y = (A+B)'", "nor", "nor"),
        ("AND = NAND + inverter", "and", "and"), ("OR = NOR + inverter", "or", "or"), ("XOR: Y = A'B + AB'", "xor", "xor"),
        ("XNOR: Y = AB + A'B'", "xnor", "xnor"), ("Transmission gate (S = 1 passes IN to OUT)", "tg", "tg"),
        ("2:1 MUX with transmission gates: S = 0 passes A, S = 1 passes B", "mux", "mux"), ("6T SRAM cell", "sram", "sram")]
HEAD = ParagraphStyle("g", fontName="Helvetica-Bold", fontSize=10.5, leading=13, spaceBefore=4, spaceAfter=2)


def row(title, g, st):
    t = Table([[fit("gate_" + g), fit("stick_" + st)]], colWidths=[13.7 * cm, 13.7 * cm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                           ("LINEBELOW", (0, 0), (-1, 0), 0.4, colors.HexColor("#cccccc"))]))
    return [Paragraph(title, HEAD), t]


fl = [Paragraph("CMOS Circuit Diagram (left) and Stick Diagram (right)", H1),
      Paragraph("Each gate has a PMOS pull-up network to VDD and an NMOS pull-down network to GND. Stick-diagram colours: <font color='#2eaa3c'><b>green</b></font> n-diffusion, <font color='#e8a317'><b>orange</b></font> p-diffusion, <font color='#d62828'><b>red</b></font> poly, <font color='#2f5be7'><b>blue</b></font> metal, black squares are contacts; a transistor forms where poly crosses diffusion. <b>Draw it:</b> rails, diffusion strips, poly per input, contacts and metal, then check series/parallel against the logic.", NOTE)]
for i, r in enumerate(ROWS):
    if i in (2, 4, 6, 8): fl.append(PageBreak())
    fl += row(*r)
SimpleDocTemplate(OUT, pagesize=landscape(A4), leftMargin=1.2 * cm, rightMargin=1.2 * cm, topMargin=1.1 * cm, bottomMargin=1.0 * cm, title="Gate and Stick Diagrams").build(fl)
r = pypdf.PdfReader(SRC); a = pypdf.PdfReader(OUT); w = pypdf.PdfWriter()
for i, p in enumerate(r.pages):
    w.add_page(p)
    if i == 13:  # last VLSI page
        for q in a.pages: w.add_page(q)
w.write(FINAL); print(len(r.pages), "+", len(a.pages))
