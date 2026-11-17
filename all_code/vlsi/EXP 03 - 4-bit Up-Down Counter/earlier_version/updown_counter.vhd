-- EXP 03 - 4-bit up/down counter (design: updown_counter.vhd, testbench: updown_counter_tb.vhd, board top: counter_top.vhd)
--
-- STEPS (Vivado)
--  1. File > Project > New > RTL Project. Tick 'Do not specify sources at this time'.
--     Part: xc7s50csga324-1  (Boolean Board, Spartan-7 XC7S50CSGA324-1)  (or pick the 'Boolean Board' if the board files are installed).
--  2. Add Sources > Add or create design sources > add the design .vhd (and counter_top.vhd for Exp 3).
--     Add Sources > Add or create simulation sources > add the *_tb.vhd.
--  3. In Sources > Simulation Sources, right-click the *_tb > Set as Top.
--  4. Flow Navigator > Simulation > Run Simulation > Run Behavioral Simulation. Run for 500 ns (Run All).
--     View > Zoom Fit. Change radix of buses (right-click signal > Radix) and screenshot the waveform.
--     Tcl console must print the 'PASSED' message.
--  5. RTL Analysis > Open Elaborated Design > Schematic (screenshot).
--  6. Sources > Design Sources: right-click counter_top > Set as Top.
--  7. Add Sources > Add or create constraints > add the Boolean Board master XDC (Real Digital).
--     Uncomment the lines for the ports below and rename each port in the XDC to match:
--       clk100 -> 100 MHz board clock pin (see the Boolean Board master XDC)
--       sw[0] (rst), sw[1] (en), sw[2] (up) -> SW0, SW1, SW2
--       led[3:0] -> LD3..LD0
--  8. Synthesis > Run Synthesis, then Implementation > Run Implementation, then Generate Bitstream.
--  9. Board: USB cable to the PROG/UART port, power switch ON.
-- 10. Open Hardware Manager > Open Target > Auto Connect > Program Device > Program.
-- 11. Test with the switches/buttons and watch the LEDs.
--
-- NOTE
--   Implementation top is counter_top (it adds a 100 MHz -> 1.5 Hz divider so the count is visible).
--   Simulation top is updown_counter_tb.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

-- 4-bit synchronous up/down counter: rst (sync), en, up (1 = count up, 0 = count down)
entity updown_counter is
    port (
        clk  : in  std_logic;
        rst  : in  std_logic;
        en   : in  std_logic;
        up   : in  std_logic;
        Qout : out std_logic_vector(3 downto 0)
    );
end updown_counter;

architecture Behavioral of updown_counter is
    signal cnt : unsigned(3 downto 0) := (others => '0');
begin
    process (clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                cnt <= (others => '0');
            elsif en = '1' then
                if up = '1' then
                    cnt <= cnt + 1;
                else
                    cnt <= cnt - 1;
                end if;
            end if;
        end if;
    end process;
    Qout <= std_logic_vector(cnt);
end Behavioral;
