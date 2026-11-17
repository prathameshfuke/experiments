-- EXP 03 - 4-bit binary counter with asynchronous clear (bitcounter.vhd, testbench bitcounter_test.vhd)
-- Source: faculty 'VLSI D&T Practical Manual (Error Free)'.  Verified: simulated in NVC, outputs match the expected values.
--
-- STEPS (Vivado)
--  1. File > Project > New > RTL Project, tick 'Do not specify sources'. Part: xc7s50csga324-1 (Boolean Board, Spartan-7).
--  2. Add Sources > design source: this file. Add Sources > simulation source: bitcounter_test.vhd.
--  3. Sources > Simulation Sources > right-click bitcounter_test > Set as Top.
--  4. Run Simulation > Run Behavioral Simulation, run 400 ns, View > Zoom Fit, screenshot the waveform.
--  5. RTL Analysis > Open Elaborated Design > Schematic, screenshot.
--  6. Design Sources: right-click bitcounter > Set as Top.
--  7. Add Sources > constraints: XDC with these ports (Boolean Board pins):
--       clk -> a push button (one press = one count) or a slowed clock
--       clr -> SW0 or a push button
--       q[3:0] -> LD0..LD3 (G1 G2 F1 F2)
--  8. Run Synthesis > Run Implementation > Generate Bitstream.
--  9. Board: micro-USB on PROG/UART, power ON. Hardware Manager > Open Target > Auto Connect > Program Device.
-- 10. Test with the switches / buttons and watch the LEDs.
--
-- NOTE
--   At 100 MHz the count is invisible on LEDs: use a button as clk, or divide the clock first (see earlier_version/counter_top.vhd).
--   Clock/button pins: from the Boolean Board master XDC.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity bitcounter is
    Port (
        clk : in STD_LOGIC;
        clr : in STD_LOGIC;
        q   : out STD_LOGIC_VECTOR (3 downto 0)
    );
end bitcounter;

architecture Behavioral of bitcounter is
    signal tmp : STD_LOGIC_VECTOR(3 downto 0) := "0000";
begin
    process(clk, clr)
    begin
        if clr = '1' then
            tmp <= "0000";
        elsif rising_edge(clk) then
            tmp <= std_logic_vector(unsigned(tmp) + 1);
        end if;
    end process;

    q <= tmp;
end Behavioral;
