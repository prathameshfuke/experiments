-- EXP 05 - 4 x 4 keypad interface (matrix_key.vhd, testbench matrix_key_tb.vhd)
-- Source: faculty 'VLSI D&T Practical Manual (Error Free)'.  Verified: simulated in NVC, outputs match the expected values.
--
-- STEPS (Vivado)
--  1. File > Project > New > RTL Project, tick 'Do not specify sources'. Part: xc7s50csga324-1 (Boolean Board, Spartan-7).
--  2. Add Sources > design source: this file. Add Sources > simulation source: matrix_key_tb.vhd.
--  3. Sources > Simulation Sources > right-click matrix_key_tb > Set as Top.
--  4. Run Simulation > Run Behavioral Simulation, run 160 us, View > Zoom Fit, screenshot the waveform.
--  5. RTL Analysis > Open Elaborated Design > Schematic, screenshot.
--  6. Design Sources: right-click matrix_key > Set as Top.
--  7. Add Sources > constraints: XDC with these ports (Boolean Board pins):
--       clk -> 100 MHz board clock
--       a[3:0] (rows, outputs) -> Pmod JA pins 1-4
--       b[3:0] (columns, inputs, PULLUP TRUE) -> Pmod JA pins 7-10
--       led[7:0] -> LD0..LD7
--  8. Run Synthesis > Run Implementation > Generate Bitstream.
--  9. Board: micro-USB on PROG/UART, power ON. Hardware Manager > Open Target > Auto Connect > Program Device.
-- 10. Test with the switches / buttons and watch the LEDs.
--
-- NOTE
--   matrix_key_tb.vhd was added here (the PDF has no testbench): it presses keys 5, B, 0 and checks the LED pattern.
--   Pmod and clock pins: from the Boolean Board master XDC.
--   Scan speed: sig1(10:8) changes every 256 clocks = 2.56 us per row phase at 100 MHz.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity matrix_key is
    port (
        clk : in std_logic;
        b   : in std_logic_vector(3 downto 0); -- columns
        a   : out std_logic_vector(3 downto 0); -- rows
        led : out std_logic_vector(7 downto 0)
    );
end matrix_key;

architecture Behavioral of matrix_key is
    signal sig1 : unsigned(29 downto 0) := (others => '0');
begin
    scan_process : process(clk)
    begin
        if rising_edge(clk) then
            sig1 <= sig1 + 1;

               case std_logic_vector(sig1(10 downto 8)) is
                   when "000" =>
                       a <= "0111"; -- row 1

                   when "001" =>
                       if b = "0111" then led <= "00110011"; -- 3
                       elsif b = "1011" then led <= "00100010"; -- 2
                       elsif b = "1101" then led <= "00010001"; -- 1
                       elsif b = "1110" then led <= "00000000"; -- 0
                       end if;

                   when "010" =>
                       a <= "1011"; -- row 2

                   when "011" =>
                       if b = "1110" then led <= "01000100"; -- 4
                       elsif b = "1101" then led <= "01010101"; -- 5
                       elsif b = "1011" then led <= "01100110"; -- 6
                       elsif b = "0111" then led <= "01110111"; -- 7
                       end if;

                   when "100" =>
                       a <= "1101"; -- row 3

                   when "101" =>
                       if b = "1110" then led <= "10001000"; -- 8
                       elsif b = "1101" then led <= "10011001"; -- 9
                       elsif b = "1011" then led <= "10101010"; -- A
                       elsif b = "0111" then led <= "10111011"; -- B
                       end if;

                   when "110" =>
                       a <= "1110"; -- row 4

                   when "111" =>
                       if b = "1110" then led <= "11001100"; -- C
                       elsif b = "1101" then led <= "11011101"; -- D
                       elsif b = "1011" then led <= "11101110"; -- E
                       elsif b = "0111" then led <= "11111111"; -- F
                       end if;

                 when others =>
                     a <= "1111";
            end case;
        end if;
    end process;
end Behavioral;
