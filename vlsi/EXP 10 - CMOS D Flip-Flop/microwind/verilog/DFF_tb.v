`timescale 1ns/1ns
module tb;
reg d, clk; wire q, qb; dff1 dut(d, clk, q, qb);
integer bad = 0;
initial begin
 clk = 0; d = 1; #2; clk = 1; #2; if (q !== 1 || qb !== 0) bad = bad + 1;   // captures 1
 d = 0; #2; if (q !== 1) bad = bad + 1;                                   // d changes while clk high: no change
 clk = 0; #2; if (q !== 1) bad = bad + 1;                                 // falling edge: no change
 clk = 1; #2; if (q !== 0 || qb !== 1) bad = bad + 1;                    // captures 0
 d = 1; #2; clk = 0; #2; if (q !== 0) bad = bad + 1;
 if (bad == 0) $display("PASS dff1"); else $display("FAIL dff1");
end
endmodule
