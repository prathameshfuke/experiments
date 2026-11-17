-- EXP 05 - 4x4 keypad scanner (design: keypad.vhd, testbench: keypad_tb.vhd)
--
-- STEPS (Vivado)
--  1. File > Project > New > RTL Project. Tick 'Do not specify sources at this time'.
--     Part: xc7s50csga324-1  (Boolean Board, Spartan-7 XC7S50CSGA324-1)  (or pick the 'Boolean Board' if the board files are installed).
--  2. Add Sources > Add or create design sources > add the design .vhd (and counter_top.vhd for Exp 3).
--     Add Sources > Add or create simulation sources > add the *_tb.vhd.
--  3. In Sources > Simulation Sources, right-click the *_tb > Set as Top.
--  4. Flow Navigator > Simulation > Run Simulation > Run Behavioral Simulation. Run for 5 us (Run All).
--     View > Zoom Fit. Change radix of buses (right-click signal > Radix) and screenshot the waveform.
--     Tcl console must print the 'PASSED' message.
--  5. RTL Analysis > Open Elaborated Design > Schematic (screenshot).
--  6. Sources > Design Sources: right-click keypad > Set as Top.
--  7. Add Sources > Add or create constraints > add the Boolean Board master XDC (Real Digital).
--     Uncomment the lines for the ports below and rename each port in the XDC to match:
--       clk -> 100 MHz board clock
--       row[3:0] -> Pmod JA pins 1-4 (outputs)
--       col[3:0] -> Pmod JA pins 7-10 (inputs, set PULLUP TRUE in the XDC)
--       led[15:0] -> LD15..LD0
--       hex[3:0] -> not used (leave unconstrained)
--  8. Synthesis > Run Synthesis, then Implementation > Run Implementation, then Generate Bitstream.
--  9. Board: USB cable to the PROG/UART port, power switch ON.
-- 10. Open Hardware Manager > Open Target > Auto Connect > Program Device > Program.
-- 11. Test with the switches/buttons and watch the LEDs.
--
-- NOTE
--   Keypad row pins -> row[3:0], keypad column pins -> col[3:0].
--   Press key n: LED n lights and stays on.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

-- 4x4 matrix keypad scanner.
-- Rows are driven low one at a time; a pressed key pulls its column low (columns have pull-ups).
-- Key number = 4*row + col (0..F). The LED with that number lights and stays lit until
-- another key is pressed; hex shows the same key number in binary.
-- SCAN_DIV = clock cycles per row slot (100 MHz / 100_000 -> each row scanned for 1 ms).
entity keypad is
    generic (SCAN_DIV : positive := 100_000);
    port (
        clk : in  std_logic;
        row : out std_logic_vector(3 downto 0);
        col : in  std_logic_vector(3 downto 0);
        led : out std_logic_vector(15 downto 0);
        hex : out std_logic_vector(3 downto 0)
    );
end keypad;

architecture Behavioral of keypad is
    signal tick  : integer range 0 to SCAN_DIV - 1 := 0;
    signal r_idx : unsigned(1 downto 0) := (others => '0');
    signal key   : unsigned(3 downto 0) := (others => '0');
    signal led_r : std_logic_vector(15 downto 0) := (others => '0');
begin
    -- one row low at a time
    with r_idx select row <=
        "1110" when "00",
        "1101" when "01",
        "1011" when "10",
        "0111" when others;

    process (clk)
        variable k : unsigned(3 downto 0);
    begin
        if rising_edge(clk) then
            if tick = SCAN_DIV - 1 then
                tick <= 0;
                for i in 0 to 3 loop                      -- sample columns at the end of the slot
                    if col(i) = '0' then
                        k := r_idx & to_unsigned(i, 2);
                        key   <= k;
                        led_r <= (others => '0');
                        led_r(to_integer(k)) <= '1';
                    end if;
                end loop;
                r_idx <= r_idx + 1;
            else
                tick <= tick + 1;
            end if;
        end if;
    end process;

    led <= led_r;
    hex <= std_logic_vector(key);
end Behavioral;
