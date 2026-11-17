`timescale 1ns/1ns
module tb;
reg a, b; wire sum, carry; hadd dut(a, b, sum, carry);
integer i, bad = 0;
initial begin
 for (i = 0; i < 4; i = i + 1) begin {a, b} = i; #1; if (sum !== (a ^ b) || carry !== (a & b)) bad = bad + 1; end
 if (bad == 0) $display("PASS hadd"); else $display("FAIL hadd");
end
endmodule
