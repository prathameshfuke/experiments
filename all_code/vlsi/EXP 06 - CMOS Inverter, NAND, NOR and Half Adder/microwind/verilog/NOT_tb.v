`timescale 1ns/1ns
module tb;
reg a; wire s; inv1 dut(a, s);
integer bad = 0;
initial begin
 a = 0; #1; if (s !== 1) bad = bad + 1;
 a = 1; #1; if (s !== 0) bad = bad + 1;
 if (bad == 0) $display("PASS inv1"); else $display("FAIL inv1");
end
endmodule
