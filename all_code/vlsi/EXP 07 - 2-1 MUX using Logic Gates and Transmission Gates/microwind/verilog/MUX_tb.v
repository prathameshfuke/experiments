`timescale 1ns/1ns
module tb;
reg d0, d1, s; wire y; mux21 dut(d0, d1, s, y);
integer i, bad = 0;
initial begin
 for (i = 0; i < 8; i = i + 1) begin {s, d1, d0} = i; #1; if (y !== (s ? d1 : d0)) bad = bad + 1; end
 if (bad == 0) $display("PASS mux21"); else $display("FAIL mux21");
end
endmodule
