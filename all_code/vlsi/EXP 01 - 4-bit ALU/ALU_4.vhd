-- EXP 01 - 4-bit ALU (ALU_4.vhd, testbench ALU_4_test.vhd, pins ALU_4.xdc)
-- Source: faculty 'VLSI D&T Practical Manual (Error Free)'.  Verified: simulated in NVC, outputs match the expected values.
--
-- STEPS (Vivado)
--  1. File > Project > New > RTL Project, tick 'Do not specify sources'. Part: xc7s50csga324-1 (Boolean Board, Spartan-7).
--  2. Add Sources > design source: this file. Add Sources > simulation source: ALU_4_test.vhd.
--  3. Sources > Simulation Sources > right-click ALU_4_test > Set as Top.
--  4. Run Simulation > Run Behavioral Simulation, run 1000 ns, View > Zoom Fit, screenshot the waveform.
--  5. RTL Analysis > Open Elaborated Design > Schematic, screenshot.
--  6. Design Sources: right-click ALU_4 > Set as Top.
--  7. Add Sources > constraints: XDC with these ports (Boolean Board pins):
--       a[3:0] -> SW0..SW3 (V2 U2 U1 T2)
--       b[3:0] -> SW4..SW7 (T1 R2 R1 P2)
--       sel[2:0] -> SW8..SW10 (P1 N2 N1)
--       y[3:0] -> LD0..LD3 (G1 G2 F1 F2)
--       (all in ALU_4.xdc, use it as is)
--  8. Run Synthesis > Run Implementation > Generate Bitstream.
--  9. Board: micro-USB on PROG/UART, power ON. Hardware Manager > Open Target > Auto Connect > Program Device.
-- 10. Test with the switches / buttons and watch the LEDs.
--
-- NOTE
--   sel: 000 A+B, 001 A-B, 010 AND, 011 NAND, 100 XOR, 101 XNOR, 110 OR, 111 A.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity ALU_4 is
    Port (
        a   : in STD_LOGIC_VECTOR (3 downto 0);
        b   : in STD_LOGIC_VECTOR (3 downto 0);
        sel : in STD_LOGIC_VECTOR (2 downto 0);
        y   : out STD_LOGIC_VECTOR (3 downto 0)
    );
end ALU_4;

architecture Behavioral of ALU_4 is
begin
    process(a, b, sel)
    begin
        case sel is
            when "000" => y <= std_logic_vector(unsigned(a) + unsigned(b));
            when "001" => y <= std_logic_vector(unsigned(a) - unsigned(b));
            when "010" => y <= a and b;
            when "011" => y <= a nand b;
            when "100" => y <= a xor b;
            when "101" => y <= a xnor b;
            when "110" => y <= a or b;
            when others => y <= a;
        end case;
    end process;
end Behavioral;
