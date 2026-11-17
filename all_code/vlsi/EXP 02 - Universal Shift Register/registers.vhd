-- EXP 02 - Universal shift register (registers.vhd, testbench shiftregister.vhd)
-- Source: faculty 'VLSI D&T Practical Manual (Error Free)'.  Verified: simulated in NVC, outputs match the expected values.
--
-- STEPS (Vivado)
--  1. File > Project > New > RTL Project, tick 'Do not specify sources'. Part: xc7s50csga324-1 (Boolean Board, Spartan-7).
--  2. Add Sources > design source: this file. Add Sources > simulation source: shiftregister.vhd.
--  3. Sources > Simulation Sources > right-click shiftregister > Set as Top.
--  4. Run Simulation > Run Behavioral Simulation, run 1100 ns, View > Zoom Fit, screenshot the waveform.
--  5. RTL Analysis > Open Elaborated Design > Schematic, screenshot.
--  6. Design Sources: right-click registers > Set as Top.
--  7. Add Sources > constraints: XDC with these ports (Boolean Board pins):
--       clk -> a push button (BTN0)
--       rst -> a push button (BTN3)
--       mode[1:0] -> SW1, SW0
--       il, ir -> SW2, SW3
--       i[3:0] -> SW7..SW4 (T1 R2 R1 P2)
--       q[3:0] -> LD0..LD3 (G1 G2 F1 F2)
--  8. Run Synthesis > Run Implementation > Generate Bitstream.
--  9. Board: micro-USB on PROG/UART, power ON. Hardware Manager > Open Target > Auto Connect > Program Device.
-- 10. Test with the switches / buttons and watch the LEDs.
--
-- NOTE
--   mode: 00 hold, 01 parallel load, 10 shift left (ir in), 11 shift right (il in). rst clears asynchronously.
--   Button and extra switch pins: take them from the Boolean Board master XDC (the PDF only gives the ALU pins).

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity registers is
    Port (
        clk : in STD_LOGIC;
        il   : in STD_LOGIC;
        ir   : in STD_LOGIC;
        rst : in STD_LOGIC;
        mode : in STD_LOGIC_VECTOR (1 downto 0);
        i    : in STD_LOGIC_VECTOR (3 downto 0);
        q    : out STD_LOGIC_VECTOR (3 downto 0)
    );
end registers;

architecture Behavioral of registers is
    signal qtmp : STD_LOGIC_VECTOR(3 downto 0) := "0000";
begin
    process(clk, rst)
    begin
        if rst = '1' then
            qtmp <= "0000";
        elsif rising_edge(clk) then
            case mode is
                 when "00" => qtmp <= qtmp;                  -- Hold
                 when "01" => qtmp <= i;                     -- Parallel load
                 when "10" => qtmp <= qtmp(2 downto 0) & ir; -- Left shift
                 when "11" => qtmp <= il & qtmp(3 downto 1); -- Right shift
                 when others => qtmp <= qtmp;
            end case;
        end if;
    end process;

    q <= qtmp;
end Behavioral;
