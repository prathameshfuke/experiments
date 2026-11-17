"""Build the GitHub Pages download site into docs/ (index.html, per-experiment zips, study notes).
Run from the repo root:  python3 tools/build_site.py
Pages setting: branch main, folder /docs. "Download everything" uses GitHub's own always-current archive zip."""
import html, json, os, shutil, urllib.parse, zipfile

OWNER, REPO = "prathameshfuke", "experiments"
RAW = "https://github.com/%s/%s/raw/main/" % (OWNER, REPO)
TREE = "https://github.com/%s/%s/tree/main/" % (OWNER, REPO)
ALL_ZIP = "https://github.com/%s/%s/archive/refs/heads/main.zip" % (OWNER, REPO)
OUT, DL = "docs", "docs/downloads"
q = lambda p: urllib.parse.quote(p)


def slug(subject, name):
    return (subject + "_" + name.split(" - ")[0]).replace(" ", "_")


def zip_dir(src, dst):
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(src):
            for f in files:
                if f == ".DS_Store": continue
                p = os.path.join(root, f); z.write(p, os.path.relpath(p, os.path.dirname(src)))


def experiments(subject):
    rows = []
    for e in sorted(os.listdir(subject)):
        p = os.path.join(subject, e)
        if not (e.startswith("EXP") and os.path.isdir(p)): continue
        files = []
        for d in (p, os.path.join(p, "docx")):
            if os.path.isdir(d):
                for f in sorted(os.listdir(d)):
                    if f.endswith((".pdf", ".docx")):
                        short = f.replace("VLSI D&T ", "").rsplit(".", 1)[0]
                        files.append({"label": short if len(os.listdir(d)) > 3 else f.rsplit(".", 1)[1].upper(),
                                      "kind": f.rsplit(".", 1)[1], "name": f, "href": RAW + q(os.path.join(d, f))})
        z = slug(subject.upper(), e) + ".zip"; zip_dir(p, os.path.join(DL, z))
        rows.append({"subject": subject.upper(), "name": e, "files": files, "zip": "downloads/" + z,
                     "zip_kb": os.path.getsize(os.path.join(DL, z)) // 1024, "folder": TREE + q(p)})
    return rows


os.makedirs(DL, exist_ok=True)
for f in os.listdir(DL): os.remove(os.path.join(DL, f))
data = {"vlsi": experiments("vlsi"), "miot": experiments("miot")}
notes = []
for f in sorted(os.listdir("study_notes")):
    if f.endswith(".pdf"):
        shutil.copy(os.path.join("study_notes", f), os.path.join(DL, f.replace(" ", "_").replace("&", "and")))
        notes.append({"name": f[:-4], "href": "downloads/" + urllib.parse.quote(f.replace(" ", "_").replace("&", "and"))})
extra = [{"name": "Microwind layouts (.MSK) - ZIP", "href": RAW + "zips/Microwind_exp.zip"},
         {"name": "All VLSI code - ZIP", "href": RAW + "zips/VLSI_all_code.zip"},
         {"name": "All MIOT code - ZIP", "href": RAW + "zips/MIOT_all_code.zip"},
         {"name": "VLSI lab manuals (PDF)", "href": TREE + "vlsi/lab_manual"}, {"name": "MIOT lab manuals (PDF)", "href": TREE + "miot/lab_manual"}]

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VLSI and MIOT Lab Downloads</title>
<meta name="description" content="Documents, code and Microwind files for the VLSI D&amp;T and MIOT lab experiments. One-click downloads.">
<style>
:root{--bg:#f7f8fa;--card:#fff;--ink:#16202b;--mute:#5b6773;--line:#e1e5ea;--acc:#1d4ed8;--accink:#fff;--chip:#eef2ff}
@media (prefers-color-scheme:dark){:root{--bg:#0f141a;--card:#171e26;--ink:#e8edf2;--mute:#9aa7b4;--line:#2a3541;--acc:#6ea0ff;--accink:#0b1220;--chip:#1c2740}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:980px;margin:0 auto;padding:32px 16px 64px}h1{font-size:1.9rem;margin:0 0 6px}h2{font-size:1.2rem;margin:36px 0 10px}
p.sub{color:var(--mute);margin:0 0 22px}a{color:var(--acc)}
.hero{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.hero div{flex:1;min-width:220px}.hero b{font-size:1.1rem}.hero span{display:block;color:var(--mute);font-size:.92rem}
.btn{display:inline-block;background:var(--acc);color:var(--accink);text-decoration:none;font-weight:600;padding:10px 16px;border-radius:10px}
.btn.big{padding:14px 22px;font-size:1.05rem}.chip{display:inline-block;background:var(--chip);color:var(--acc);text-decoration:none;font-size:.88rem;padding:4px 10px;border-radius:999px;margin:2px 4px 2px 0}
.chip:hover,.btn:hover{filter:brightness(1.08)}
input[type=search]{width:100%;padding:11px 14px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink);font-size:1rem;margin:6px 0 4px}
.row{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:8px 0;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.row .t{flex:1 1 280px;font-weight:600}.row .t small{display:block;color:var(--mute);font-weight:400}
.row .l{display:flex;flex-wrap:wrap;align-items:center}.hide{display:none}footer{margin-top:40px;color:var(--mute);font-size:.9rem}
</style></head><body><main>
<h1>VLSI D&amp;T and MIOT Lab Experiments</h1>
<p class="sub">Documents, code, simulation images and Microwind files. Pick an experiment below, or grab everything at once.</p>
<div class="hero"><div><b>Download everything</b><span>All experiments, PDFs, Word docs, code, images and Microwind files in one ZIP (always the latest version).</span></div>
<a class="btn big" href="__ALL__">Download all (ZIP)</a></div>
<h2>Study notes</h2><div class="row"><div class="t">Theory, steps and viva questions<small>VLSI notes include the CMOS gate circuits and stick diagrams</small></div><div class="l" id="notes"></div></div>
<input type="search" id="q" placeholder="Search experiments (e.g. NAND, ALU, DHT11, SRAM)" aria-label="Search experiments">
<h2>VLSI D&amp;T</h2><div id="vlsi"></div>
<h2>MIOT</h2><div id="miot"></div>
<h2>More files</h2><div class="row"><div class="l" id="extra"></div></div>
<footer>Source: <a href="https://github.com/__OWNER__/__REPO__">github.com/__OWNER__/__REPO__</a>. Each experiment ZIP holds its PDF, Word doc, code, images and Microwind files. Credentials in the code are placeholders.</footer>
</main>
<script>
const D=__DATA__;
const esc=s=>s.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const chip=(h,t)=>'<a class="chip" href="'+h+'">'+esc(t)+'</a>';
document.getElementById("notes").innerHTML=D.notes.map(n=>chip(n.href,n.name)).join("");
document.getElementById("extra").innerHTML=D.extra.map(n=>chip(n.href,n.name)).join("");
function rows(id,list){document.getElementById(id).innerHTML=list.map(e=>
 '<div class="row" data-s="'+esc((e.name+" "+e.files.map(f=>f.name).join(" ")).toLowerCase())+'"><div class="t">'+esc(e.name)+'<small>'+e.zip_kb+' KB ZIP</small></div><div class="l">'+
 '<a class="btn" href="'+e.zip+'">Download ZIP</a>&nbsp; '+e.files.map(f=>chip(f.href,f.label)).join("")+chip(e.folder,"Browse files")+'</div></div>').join("")}
rows("vlsi",D.vlsi);rows("miot",D.miot);
document.getElementById("q").addEventListener("input",ev=>{const v=ev.target.value.toLowerCase().trim();
 document.querySelectorAll(".row[data-s]").forEach(r=>r.classList.toggle("hide",v&&!r.dataset.s.includes(v)))});
</script></body></html>
"""
page = (PAGE.replace("__DATA__", json.dumps({**data, "notes": notes, "extra": extra})).replace("__ALL__", ALL_ZIP)
        .replace("__OWNER__", OWNER).replace("__REPO__", REPO))
open(os.path.join(OUT, "index.html"), "w").write(page)
open(os.path.join(OUT, ".nojekyll"), "w").close()
print("site built:", len(data["vlsi"]) + len(data["miot"]), "experiment zips,", len(notes), "notes PDFs")
