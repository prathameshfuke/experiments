"""Build the GitHub Pages download site into docs/ (index.html, per-experiment zips, study notes).
Run from the repo root:  python3 tools/build_site.py
Pages setting: branch main, folder /docs. "Download everything" uses GitHub's own always-current archive zip.
The page markup lives in tools/site_template.html (placeholders __DATA__ and __REPO__)."""
import json, math, os, re, shutil, urllib.parse, zipfile

OWNER, REPO = "prathameshfuke", "experiments"
REPO_URL = "https://github.com/%s/%s" % (OWNER, REPO)
RAW, TREE = REPO_URL + "/raw/main/", REPO_URL + "/tree/main/"
ALL_ZIP = REPO_URL + "/archive/refs/heads/main.zip"
OUT, DL = "docs", "docs/downloads"
q = lambda p: urllib.parse.quote(p)

META = {  # (subject, exp code): (description, tags)
    ("VLSI", "01"): ("Add, subtract, logic operations and pass-through, chosen by a 3-bit select code.", ["VHDL", "Vivado", "Boolean Board"]),
    ("VLSI", "02"): ("Parallel load, shift left, shift right and hold in one register.", ["VHDL", "Vivado", "Boolean Board"]),
    ("VLSI", "03"): ("Counts up or down on each clock, with reset and enable.", ["VHDL", "Vivado", "Boolean Board"]),
    ("VLSI", "04"): ("Write and read in order, with full and empty flags.", ["VHDL", "Vivado", "Boolean Board"]),
    ("VLSI", "05"): ("Scan the keypad and show the pressed key on LEDs and a hex display.", ["VHDL", "Vivado", "Boolean Board"]),
    ("VLSI", "06"): ("Microwind layouts and transients for each gate, with and without load capacitance. One report per gate.", ["Microwind", "Verilog"]),
    ("VLSI", "07"): ("2-to-1 multiplexer built from logic gates and from transmission gates.", ["Microwind", "Verilog"]),
    ("VLSI", "08"): ("Layout plus write, hold and read waveforms.", ["Microwind", "Verilog"]),
    ("VLSI", "10"): ("Layout of an edge-triggered D flip-flop.", ["Microwind", "Verilog"]),
    ("MIOT", "02"): ("Blink an LED and read a push button on an Arduino Uno.", ["Arduino Uno"]),
    ("MIOT", "03"): ("Read temperature and humidity from a DHT11 on an Arduino Uno.", ["Arduino Uno"]),
    ("MIOT", "04"): ("Drive a stepper motor through an L293D from an Arduino Uno.", ["Arduino Uno"]),
    ("MIOT", "05"): ("Send DHT11 readings from a NodeMCU to ThingSpeak.", ["NodeMCU", "ThingSpeak", "MQTT"]),
    ("MIOT", "06"): ("A Flask web page that switches a bulb over the local network.", ["Raspberry Pi", "Flask"]),
    ("MIOT", "07"): ("Switch an LED from a phone over an HC-05 Bluetooth module.", ["Arduino Uno", "Bluetooth"]),
    ("MIOT", "08"): ("Send data from an Arduino to a Raspberry Pi over XBee (ZigBee).", ["Arduino Uno", "Raspberry Pi", "XBee"]),
    ("MIOT", "09A"): ("Log weather data on a Raspberry Pi to ThingSpeak and e-mail an alert.", ["Raspberry Pi", "ThingSpeak"]),
    ("MIOT", "09B"): ("Record RFID attendance on a Raspberry Pi with an EM-18 reader.", ["Raspberry Pi", "RFID"]),
    ("MIOT", "09C"): ("RFID attendance with an Arduino Uno, an MFRC522 reader and an ESP8266.", ["Arduino Uno", "RFID", "ESP8266"]),
    ("MIOT", "09D"): ("Control home appliances from the Blynk app with a NodeMCU.", ["NodeMCU", "Blynk"]),
}


def zip_dir(src, dst):
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(src):
            for f in files:
                if f != ".DS_Store":
                    p = os.path.join(root, f); z.write(p, os.path.relpath(p, os.path.dirname(src)))


def kb(p): return max(1, math.ceil(os.path.getsize(p) / 1024))


def files_in(folder, exts, skip=()):
    out = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if d not in skip)
        for f in sorted(files):
            if f.lower().endswith(exts):
                p = os.path.join(root, f); out.append({"name": re.sub(r"^VLSI D&T EXP \d+ - ", "", f), "href": RAW + q(p), "kb": kb(p)})
    return out


def experiments(subject):
    rows = []
    for e in sorted(os.listdir(subject)):
        p = os.path.join(subject, e)
        if not (e.startswith("EXP") and os.path.isdir(p)): continue
        num = e.split(" - ")[0].replace("EXP ", "")
        desc, tags = META[(subject.upper(), num)]
        groups = []
        docs = files_in(p, (".pdf", ".docx"), skip=("code", "img", "microwind", "earlier_version"))
        if docs: groups.append({"name": "Reports (PDF and Word)", "files": docs})
        code = files_in(os.path.join(p, "code") if os.path.isdir(os.path.join(p, "code")) else p, (".vhd", ".xdc", ".py", ".sh", ".ino"),
                        skip=("earlier_version", "img", "docx", "microwind"))
        if code: groups.append({"name": "Code", "files": code})
        mw = files_in(os.path.join(p, "microwind"), (".msk",), skip=("verilog",)) if os.path.isdir(os.path.join(p, "microwind")) else []
        if mw: groups.append({"name": "Microwind layouts", "files": mw})
        vl = files_in(os.path.join(p, "microwind", "verilog"), (".txt", ".v")) if os.path.isdir(os.path.join(p, "microwind", "verilog")) else []
        if vl: groups.append({"name": "Verilog for Microwind", "files": vl})
        ev = os.path.join(p, "earlier_version")
        old = files_in(ev, (".vhd", ".py", ".ino", ".sh", ".xdc")) if os.path.isdir(ev) else []
        if old: groups.append({"name": "Earlier versions", "files": old})
        img = os.path.join(p, "img"); n_img = len([f for f in os.listdir(img) if f.endswith(".png")]) if os.path.isdir(img) else 0
        z = ("%s_EXP_%s.zip" % (subject.upper(), num))
        zip_dir(p, os.path.join(DL, z))
        rows.append({"id": "%s-%s" % (subject, num.lower()), "subject": subject.upper(), "code": "EXP " + num, "title": e.split(" - ", 1)[1],
                     "desc": desc, "tags": tags, "zip": "downloads/" + z, "zip_kb": kb(os.path.join(DL, z)), "groups": groups,
                     "images": {"count": n_img, "href": TREE + q(img)} if n_img else None, "folder": TREE + q(p)})
    return rows


os.makedirs(DL, exist_ok=True)
for f in os.listdir(DL): os.remove(os.path.join(DL, f))
exps = experiments("vlsi") + experiments("miot")
notes = []
for f in sorted(os.listdir("study_notes")):
    if f.endswith(".pdf") and f != "VLSI and MIOT Study Notes.pdf":   # the combined PDF is no longer offered on the site
        dst = f.replace(" ", "_").replace("&", "and"); shutil.copy(os.path.join("study_notes", f), os.path.join(DL, dst))
        notes.append({"name": f[:-4], "href": "downloads/" + q(dst)})
extra = [{"name": "Microwind layouts (ZIP)", "href": RAW + "zips/Microwind_exp.zip"},
         {"name": "All VLSI code (ZIP)", "href": RAW + "zips/VLSI_all_code.zip"},
         {"name": "All MIOT code (ZIP)", "href": RAW + "zips/MIOT_all_code.zip"},
         {"name": "VLSI lab manuals", "href": TREE + "vlsi/lab_manual"}, {"name": "MIOT lab manuals", "href": TREE + "miot/lab_manual"}]
data = {"all_zip": ALL_ZIP, "notes": notes, "extra": extra, "exps": exps}
page = open("tools/site_template.html").read().replace("__DATA__", json.dumps(data)).replace("__REPO__", REPO_URL)
open(os.path.join(OUT, "index.html"), "w").write(page)
open(os.path.join(OUT, ".nojekyll"), "w").close()
print("site built:", len(exps), "experiments,", len(notes), "notes PDFs")
