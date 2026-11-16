-- EXP 01 - 4-bit ALU (design: alu4bit.vhd, testbench: alu4bit_tb.vhd)
--
-- STEPS (Vivado)
--  1. File > Project > New > RTL Project. Tick 'Do not specify sources at this time'.
--     Part: xc7s50csga324-1  (Boolean Board, Spartan-7 XC7S50CSGA324-1)  (or pick the 'Boolean Board' if the board files are installed).
--  2. Add Sources > Add or create design sources > add the design .vhd (and counter_top.vhd for Exp 3).
--     Add Sources > Add or create simulation sources > add the *_tb.vhd.
--  3. In Sources > Simulation Sources, right-click the *_tb > Set as Top.
--  4. Flow Navigator > Simulation > Run Simulation > Run Behavioral Simulation. Run for 160 ns (Run All).
--     View > Zoom Fit. Change radix of buses (right-click signal > Radix) and screenshot the waveform.
--     Tcl console must print the 'PASSED' message.
--  5. RTL Analysis > Open Elaborated Design > Schematic (screenshot).
--  6. Sources > Design Sources: right-click alu4bit > Set as Top.
--  7. Add Sources > Add or create constraints > add the Boolean Board master XDC (Real Digital).
--     Uncomment the lines for the ports below and rename each port in the XDC to match:
--       A[3:0] -> SW3..SW0
--       B[3:0] -> SW7..SW4
--       S[2:0] -> SW10..SW8
--       Y[3:0] -> LD3..LD0
--  8. Synthesis > Run Synthesis, then Implementation > Run Implementation, then Generate Bitstream.
--  9. Board: USB cable to the PROG/UART port, power switch ON.
-- 10. Open Hardware Manager > Open Target > Auto Connect > Program Device > Program.
-- 11. Test with the switches/buttons and watch the LEDs.
--
-- NOTE
--   S: 000 A+B, 001 A-B, 010 AND, 011 OR, 100 pass B, 101 XOR, 110 B-A, 111 pass A.
--   Combinational design: no clock needed.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity alu4bit is
    port (
        A : in  std_logic_vector(3 downto 0);
        B : in  std_logic_vector(3 downto 0);
        S : in  std_logic_vector(2 downto 0);
        Y : out std_logic_vector(3 downto 0)
    );
end alu4bit;

architecture Behavioral of alu4bit is
begin
    process (A, B, S)
        variable ua : unsigned(3 downto 0);
        variable ub : unsigned(3 downto 0);
    begin
        ua := unsigned(A);
        ub := unsigned(B);
        case S is
            when "000"  => Y <= std_logic_vector(ua + ub);  -- A + B
            when "001"  => Y <= std_logic_vector(ua - ub);  -- A - B
            when "010"  => Y <= A and B;                    -- A AND B
            when "011"  => Y <= A or B;                     -- A OR B
            when "100"  => Y <= B;                          -- Pass B
            when "101"  => Y <= A xor B;                    -- A XOR B
            when "110"  => Y <= std_logic_vector(ub - ua);  -- B - A
            when others => Y <= A;                          -- Pass A
        end case;
    end process;
end Behavioral;
