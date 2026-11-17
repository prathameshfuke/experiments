"""Render each VLSI D&T EXP *.docx to PDF (reportlab), reading the docx in document order so docx and PDF stay in sync."""
import glob, io, os
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph as P, Spacer, Image, Table as RT, TableStyle, Preformatted
from reportlab.lib.utils import ImageReader
from xml.sax.saxutils import escape

N = ParagraphStyle("n", fontName="Helvetica", fontSize=10.5, leading=14, spaceAfter=4)
T = ParagraphStyle("t", parent=N, fontName="Helvetica-Bold", fontSize=16, leading=20, spaceAfter=6)
H = ParagraphStyle("h", parent=N, fontName="Helvetica-Bold", fontSize=12.5, spaceBefore=10, keepWithNext=1)
C = ParagraphStyle("c", parent=N, fontName="Helvetica-Oblique", fontSize=9, alignment=1, spaceAfter=8)
I = ParagraphStyle("i", parent=N, fontName="Helvetica-Oblique")
B = ParagraphStyle("b", parent=N, leftIndent=14, bulletIndent=2)
CODE = ParagraphStyle("code", fontName="Courier", fontSize=7.8, leading=9.2, backColor=colors.HexColor("#F2F2F2"))
W = A4[0] - 4 * cm
NS_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NS_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
NS_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
NS_D = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"

def build(path):
    d = Document(path); out = os.path.join(os.path.dirname(os.path.dirname(path)), os.path.basename(path)[:-5] + ".pdf"); flow = []; codebuf = []
    def flush():
        if codebuf:
            flow.append(Preformatted("\n".join(codebuf), CODE)); flow.append(Spacer(1, 4)); codebuf.clear()
    for el in d.element.body.iterchildren():
        tag = el.tag.split("}")[1]
        if tag == "tbl":
            flush(); t = Table(el, d)
            cs = ParagraphStyle("tc", parent=N, fontSize=9, leading=11)
            data = [[P(escape(c.text), cs) for c in r.cells] for r in t.rows]
            rt = RT(data, colWidths=[W / len(data[0])] * len(data[0]), repeatRows=1)
            rt.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
                                    ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            flow += [rt, Spacer(1, 8)]
        elif tag == "p":
            p = Paragraph(el, d); text = p.text
            blips = el.findall(".//" + NS_A + "blip")
            if blips:
                flush()
                blob = d.part.related_parts[blips[0].get(NS_R + "embed")].blob
                iw, ih = ImageReader(io.BytesIO(blob)).getSize()
                w = min(int(el.find(".//" + NS_D + "extent").get("cx")) / 12700, W)
                flow.append(Image(io.BytesIO(blob), width=w, height=w * ih / iw, hAlign="CENTER"))
            elif p._p.pPr is not None and p._p.pPr.find(NS_W + "shd") is not None:
                codebuf.append(text.rstrip())
            else:
                flush()
                if not text.strip(): continue
                r0 = p.runs[0] if p.runs else None; e = escape(text)
                if p.style.name == "List Bullet": flow.append(P(e, B, bulletText="•"))
                elif r0 is not None and r0.font.size and r0.font.size.pt == 16: flow.append(P(e, T))
                elif r0 is not None and r0.bold: flow.append(P(e, H))
                elif r0 is not None and r0.italic and r0.font.size: flow.append(P(e, C))
                elif r0 is not None and r0.italic: flow.append(P(e, I))
                else: flow.append(P(e, N))
    flush()
    SimpleDocTemplate(out, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                      title=path.split("/")[-1][:-5]).build(flow)

import sys
for f in (sys.argv[1:] or sorted(glob.glob("EXP */docx/VLSI D&T EXP *.docx"))): build(f)
print("pdfs built")
