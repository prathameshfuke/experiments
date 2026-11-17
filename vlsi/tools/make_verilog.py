"""Write the Microwind Verilog files (primitive-based, the style used in the Microwind manual) and check them with Icarus Verilog.
Run from vlsi/:  python3 tools/make_verilog.py        (needs `iverilog` and `vvp` on PATH for the check)
Output per circuit, in EXP NN/microwind/verilog/:  <NAME>.TXT (load in Microwind)  and  <NAME>_tb.v (self-checking testbench).
Microwind itself is not run here: the check is a logic simulation of the same netlist."""
import glob, os, subprocess, sys, tempfile

HEAD = """// {name}.TXT - gate-level Verilog for Microwind (primitive style, as in the Microwind manual)
// 1) Start Microwind, File > Select Foundry > cmos012.RUL.
// 2) Compile > Compile Verilog File, choose this {name}.TXT, click Compile (layout is generated).
// 3) Simulate > Start Simulation to see the timing diagram.
"""

# name: (experiment number, module name, module text, testbench body)
CIRCUITS = {
    "NOT": ("06", "inv1", """module inv1(a, s);
 input a;
 output s;
 not not1(s, a);
endmodule
""", """reg a; wire s; inv1 dut(a, s);
integer bad = 0;
initial begin
 a = 0; #1; if (s !== 1) bad = bad + 1;
 a = 1; #1; if (s !== 0) bad = bad + 1;
 if (bad == 0) $display("PASS inv1"); else $display("FAIL inv1");
end"""),
    "NAND": ("06", "nand2", """module nand2(a, b, s);
 input a, b;
 output s;
 nand nand1(s, a, b);
endmodule
""", """reg a, b; wire s; nand2 dut(a, b, s);
integer i, bad = 0;
initial begin
 for (i = 0; i < 4; i = i + 1) begin {a, b} = i; #1; if (s !== ~(a & b)) bad = bad + 1; end
 if (bad == 0) $display("PASS nand2"); else $display("FAIL nand2");
end"""),
    "NOR": ("06", "nor2", """module nor2(a, b, s);
 input a, b;
 output s;
 nor nor1(s, a, b);
endmodule
""", """reg a, b; wire s; nor2 dut(a, b, s);
integer i, bad = 0;
initial begin
 for (i = 0; i < 4; i = i + 1) begin {a, b} = i; #1; if (s !== ~(a | b)) bad = bad + 1; end
 if (bad == 0) $display("PASS nor2"); else $display("FAIL nor2");
end"""),
    "HALFADDER": ("06", "hadd", """module hadd(a, b, sum, carry);
 input a, b;
 output sum, carry;
 xor xor1(sum, a, b);
 and and1(carry, a, b);
endmodule
""", """reg a, b; wire sum, carry; hadd dut(a, b, sum, carry);
integer i, bad = 0;
initial begin
 for (i = 0; i < 4; i = i + 1) begin {a, b} = i; #1; if (sum !== (a ^ b) || carry !== (a & b)) bad = bad + 1; end
 if (bad == 0) $display("PASS hadd"); else $display("FAIL hadd");
end"""),
    "MUX": ("07", "mux21", """module mux21(d0, d1, s, y);
 input d0, d1, s;
 output y;
 wire sb, w1, w2;
 not not1(sb, s);
 nand nand1(w1, d1, s);
 nand nand2(w2, d0, sb);
 nand nand3(y, w1, w2);
endmodule
""", """reg d0, d1, s; wire y; mux21 dut(d0, d1, s, y);
integer i, bad = 0;
initial begin
 for (i = 0; i < 8; i = i + 1) begin {s, d1, d0} = i; #1; if (y !== (s ? d1 : d0)) bad = bad + 1; end
 if (bad == 0) $display("PASS mux21"); else $display("FAIL mux21");
end"""),
    "SRAM": ("08", "sram1", """// Storage cell for the layout compiler: NOR latch set/reset by the word line and the two bit lines.
// (The 6T transistor-level cell is the hand-drawn SRAM.MSK; the compiler builds the logic function from gates.)
module sram1(wl, bl, blb, q, qb);
 input wl, bl, blb;
 output q, qb;
 wire set, rst;
 and and1(set, wl, bl);
 and and2(rst, wl, blb);
 nor nor1(q, rst, qb);
 nor nor2(qb, set, q);
endmodule
""", """reg wl, bl, blb; wire q, qb; sram1 dut(wl, bl, blb, q, qb);
integer bad = 0;
initial begin
 wl = 1; bl = 0; blb = 1; #2; if (q !== 0 || qb !== 1) bad = bad + 1;   // write 0
 wl = 0; bl = 1; blb = 0; #2; if (q !== 0 || qb !== 1) bad = bad + 1;   // hold (bit lines change, wl low)
 wl = 1; bl = 1; blb = 0; #2; if (q !== 1 || qb !== 0) bad = bad + 1;   // write 1
 wl = 0; bl = 0; blb = 1; #2; if (q !== 1 || qb !== 0) bad = bad + 1;   // hold 1
 if (bad == 0) $display("PASS sram1"); else $display("FAIL sram1");
end"""),
    "DFF": ("10", "dff1", """// Positive-edge D flip-flop from six NAND gates.
module dff1(d, clk, q, qb);
 input d, clk;
 output q, qb;
 wire n1, n2, n3, n4;
 nand nand1(n1, n4, n2);
 nand nand2(n2, n1, clk);
 nand nand3(n3, n2, clk, n4);
 nand nand4(n4, n3, d);
 nand nand5(q, n2, qb);
 nand nand6(qb, q, n3);
endmodule
""", """reg d, clk; wire q, qb; dff1 dut(d, clk, q, qb);
integer bad = 0;
initial begin
 clk = 0; d = 1; #2; clk = 1; #2; if (q !== 1 || qb !== 0) bad = bad + 1;   // captures 1
 d = 0; #2; if (q !== 1) bad = bad + 1;                                   // d changes while clk high: no change
 clk = 0; #2; if (q !== 1) bad = bad + 1;                                 // falling edge: no change
 clk = 1; #2; if (q !== 0 || qb !== 1) bad = bad + 1;                    // captures 0
 d = 1; #2; clk = 0; #2; if (q !== 0) bad = bad + 1;
 if (bad == 0) $display("PASS dff1"); else $display("FAIL dff1");
end"""),
}

ok = True
with tempfile.TemporaryDirectory() as tmp:
    for name, (num, mod, text, tb) in CIRCUITS.items():
        exp = glob.glob("EXP %s*" % num)[0]; d = os.path.join(exp, "microwind", "verilog"); os.makedirs(d, exist_ok=True)
        txt, tbf = os.path.join(d, name + ".TXT"), os.path.join(d, name + "_tb.v")
        open(txt, "w", newline="\r\n").write(HEAD.format(name=name) + text)
        open(tbf, "w").write("`timescale 1ns/1ns\nmodule tb;\n%s\nendmodule\n" % tb)
        sim = os.path.join(tmp, name + ".vvp")
        r = subprocess.run(["iverilog", "-g2005", "-o", sim, tbf, txt], capture_output=True, text=True)
        if r.returncode: print("COMPILE FAIL", name, r.stderr); ok = False; continue
        out = subprocess.run(["vvp", sim], capture_output=True, text=True).stdout.strip()
        print(name.ljust(10), out); ok &= out.startswith("PASS")
sys.exit(0 if ok else 1)
