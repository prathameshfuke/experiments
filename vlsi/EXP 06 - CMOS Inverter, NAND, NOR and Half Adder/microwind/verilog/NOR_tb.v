`timescale 1ns/1ns
module tb;
reg a, b; wire s; nor2 dut(a, b, s);
integer i, bad = 0;
initial begin
 for (i = 0; i < 4; i = i + 1) begin {a, b} = i; #1; if (s !== ~(a | b)) bad = bad + 1; end
 if (bad == 0) $display("PASS nor2"); else $display("FAIL nor2");
end
endmodule
