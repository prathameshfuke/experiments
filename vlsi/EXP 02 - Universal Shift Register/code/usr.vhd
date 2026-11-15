-- EXP 02 - Universal shift register (design: usr.vhd, testbench: usr_tb.vhd)
--
-- STEPS (Vivado)
--  1. File > Project > New > RTL Project. Tick 'Do not specify sources at this time'.
--     Part: xc7s50csga324-1  (Boolean Board, Spartan-7 XC7S50CSGA324-1)  (or pick the 'Boolean Board' if the board files are installed).
--  2. Add Sources > Add or create design sources > add the design .vhd (and counter_top.vhd for Exp 3).
--     Add Sources > Add or create simulation sources > add the *_tb.vhd.
--  3. In Sources > Simulation Sources, right-click the *_tb > Set as Top.
--  4. Flow Navigator > Simulation > Run Simulation > Run Behavioral Simulation. Run for 170 ns (Run All).
--     View > Zoom Fit. Change radix of buses (right-click signal > Radix) and screenshot the waveform.
--     Tcl console must print the 'PASSED' message.
--  5. RTL Analysis > Open Elaborated Design > Schematic (screenshot).
--  6. Sources > Design Sources: right-click usr > Set as Top.
--  7. Add Sources > Add or create constraints > add the Boolean Board master XDC (Real Digital).
--     Uncomment the lines for the ports below and rename each port in the XDC to match:
--       clk -> BTN0  (one press = one clock; a bouncing button may shift several times)
--       S[1:0] -> SW1, SW0
--       IL -> SW2
--       IR -> SW3
--       P[3:0] -> SW7..SW4
--       Q[3:0] -> LD3..LD0
--  8. Synthesis > Run Synthesis, then Implementation > Run Implementation, then Generate Bitstream.
--  9. Board: USB cable to the PROG/UART port, power switch ON.
-- 10. Open Hardware Manager > Open Target > Auto Connect > Program Device > Program.
-- 11. Test with the switches/buttons and watch the LEDs.
--
-- NOTE
--   S: 00 load, 01 shift right (IL in), 10 shift left (IR in), 11 hold.
--   For a debounced clock, use a divider like counter_top.vhd in Exp 3.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Universal shift register: S = 00 load, 01 shift right (IL in), 10 shift left (IR in), 11 hold
entity usr is
    port (
        clk : in  std_logic;
        S   : in  std_logic_vector(1 downto 0);
        IL  : in  std_logic;                      -- serial input for shift right
        IR  : in  std_logic;                      -- serial input for shift left
        P   : in  std_logic_vector(3 downto 0);   -- parallel input
        Q   : out std_logic_vector(3 downto 0)    -- parallel output
    );
end usr;

architecture Behavioral of usr is
    signal r : std_logic_vector(3 downto 0) := "0000";
begin
    process (clk)
    begin
        if rising_edge(clk) then
            case S is
                when "00"   => r <= P;                       -- parallel load
                when "01"   => r <= IL & r(3 downto 1);      -- shift right
                when "10"   => r <= r(2 downto 0) & IR;      -- shift left
                when others => r <= r;                       -- no change
            end case;
        end if;
    end process;
    Q <= r;
end Behavioral;
