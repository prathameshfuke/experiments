`timescale 1ns/1ns
module tb;
reg wl, bl, blb; wire q, qb; sram1 dut(wl, bl, blb, q, qb);
integer bad = 0;
initial begin
 wl = 1; bl = 0; blb = 1; #2; if (q !== 0 || qb !== 1) bad = bad + 1;   // write 0
 wl = 0; bl = 1; blb = 0; #2; if (q !== 0 || qb !== 1) bad = bad + 1;   // hold (bit lines change, wl low)
 wl = 1; bl = 1; blb = 0; #2; if (q !== 1 || qb !== 0) bad = bad + 1;   // write 1
 wl = 0; bl = 0; blb = 1; #2; if (q !== 1 || qb !== 0) bad = bad + 1;   // hold 1
 if (bad == 0) $display("PASS sram1"); else $display("FAIL sram1");
end
endmodule
