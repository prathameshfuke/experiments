"""Append Microwind layout views and stick/gate diagrams to the Microwind experiment docs (06, 07, 08, 10).
Run from vlsi/:  python3 tools/add_layouts.py <diagram_dir>   (diagram_dir from gate_diagrams.py)
Then:            python3 tools/build_pdfs.py <docx...>  to regenerate the PDFs."""
import glob, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from docx import Document
from docx.shared import Cm, Pt
from layout_render import render

GD = sys.argv[1]
PLAN = {  # exp number -> [(kind, source, caption)]
    "06": [("msk", "NOT", "Layout view of the CMOS inverter (NOT.MSK): N-well, P+/N+ diffusion, poly gate, metal 1 and contacts."),
           ("msk", "NAND", "Layout view of the 2-input NAND (NAND.MSK): two poly gates, parallel PMOS, series NMOS."),
           ("msk", "NOR", "Layout view of the 2-input NOR (NOR.MSK): series PMOS, parallel NMOS."),
           ("msk", "HALFADDER", "Layout view of the half adder (HALFADDER.MSK): Sum and Carry outputs.")],
    "07": [("msk", "MUX", "Layout view of the 2-to-1 multiplexer (MUX.MSK).")],
    "08": [("msk", "SRAM", "Layout view of the 6T SRAM cell (SRAM.MSK).")],
    "10": [("msk", "DFF", "Layout view of the CMOS D flip-flop (DFF.MSK).")],
}
MARK = "Microwind layout view"

for num, items in PLAN.items():
    exp = glob.glob("EXP %s*" % num)[0]
    found = glob.glob(os.path.join(exp, "docx", "VLSI D&T EXP *.docx"))
    if found:
        docx = found[0]; d = Document(docx)
    else:  # EXP 10 has no document yet: create a short one
        os.makedirs(os.path.join(exp, "docx"), exist_ok=True); docx = os.path.join(exp, "docx", "VLSI D&T %s.docx" % exp); d = Document()
        t = d.add_paragraph().add_run("VLSI D&T %s" % exp); t.bold = True; t.font.size = Pt(16)
        d.add_paragraph().add_run("Aim: draw and study the layout of a CMOS D flip-flop in Microwind.").italic = True
        r = d.add_paragraph().add_run("Steps"); r.bold = True
        for st in ("Open Microwind and load the cmos012.RUL rule file (File > Select Foundry).",
                   "File > Open > DFF.MSK from the microwind folder.",
                   "Check the design rules (Analysis > Design Rule Checker).",
                   "Simulate > Run Simulation and observe Q and Q' against D and the clock."):
            d.add_paragraph(st, style="List Bullet")
    mk = [p for p in d.paragraphs if MARK in p.text]
    if mk:  # refresh: drop the old layout section (marker paragraph and everything after it)
        body = d.element.body; cut = False
        for el in list(body):
            if el is mk[0]._p: cut = True
            if cut and not el.tag.endswith("sectPr"): body.remove(el)
    imgdir = os.path.join(exp, "img"); os.makedirs(imgdir, exist_ok=True)
    h = d.add_paragraph().add_run(MARK + "s"); h.bold = True; h.font.size = Pt(12)
    for kind, src, cap in items:
        if kind == "msk":
            out = os.path.join(imgdir, "microwind_%s.png" % src.lower())
            render(os.path.join("Microwind_exp", src + ".MSK"), out)
        else:
            out = os.path.join(imgdir, "%s.png" % src)
            shutil.copy(os.path.join(GD, src + ".png"), out)
        d.add_picture(out, width=Cm(13 if kind == "gd" else 16))
        d.paragraphs[-1].alignment = 1
        c = d.add_paragraph().add_run(cap); c.italic = True; c.font.size = Pt(9)
        d.paragraphs[-1].alignment = 1
    d.save(docx); print("updated", docx)
