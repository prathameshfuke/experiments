-- EXP 04 - 4 x 4 synchronous FIFO (fifo.vhd, testbench fifo_tb.vhd)
-- Source: faculty 'VLSI D&T Practical Manual (Error Free)'.  Verified: simulated in NVC, outputs match the expected values.
--
-- STEPS (Vivado)
--  1. File > Project > New > RTL Project, tick 'Do not specify sources'. Part: xc7s50csga324-1 (Boolean Board, Spartan-7).
--  2. Add Sources > design source: this file. Add Sources > simulation source: fifo_tb.vhd.
--  3. Sources > Simulation Sources > right-click fifo_tb > Set as Top.
--  4. Run Simulation > Run Behavioral Simulation, run 2000 ns, View > Zoom Fit, screenshot the waveform.
--  5. RTL Analysis > Open Elaborated Design > Schematic, screenshot.
--  6. Design Sources: right-click fifo > Set as Top.
--  7. Add Sources > constraints: XDC with these ports (Boolean Board pins):
--       clk -> a push button (one press = one write/read step)
--       rst -> a push button
--       enw, enr -> SW8, SW9
--       datain[3:0] -> SW0..SW3 (V2 U2 U1 T2)
--       dataout[3:0] -> LD0..LD3 (G1 G2 F1 F2)
--       empty, full -> LD4, LD5
--  8. Run Synthesis > Run Implementation > Generate Bitstream.
--  9. Board: micro-USB on PROG/UART, power ON. Hardware Manager > Open Target > Auto Connect > Program Device.
-- 10. Test with the switches / buttons and watch the LEDs.
--
-- NOTE
--   Write 4 values, full = 1. Read them back in the same order, empty = 1.
--   Button and LD4/LD5 pins: from the Boolean Board master XDC.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity fifo is
    port (
        clk     : in std_logic;
        rst     : in std_logic;
        enw     : in std_logic;
        enr     : in std_logic;
        datain : in std_logic_vector(3 downto 0);
        dataout : out std_logic_vector(3 downto 0);
        empty   : out std_logic;
        full    : out std_logic
    );
end fifo;

architecture Behavioral of fifo is
    type memory_type is array (0 to 3) of std_logic_vector(3 downto 0);
    signal memory : memory_type := (others => (others => '0'));
    signal readptr : unsigned(1 downto 0) := "00";
    signal writeptr: unsigned(1 downto 0) := "00";
    signal count    : unsigned(2 downto 0) := "000";
begin
    process(clk)
        variable do_write : boolean;
        variable do_read : boolean;
    begin
        if rising_edge(clk) then
            if rst = '1' then
                 readptr <= "00";
                 writeptr <= "00";
                 count    <= "000";
                 dataout <= (others => '0');
            else
                 do_write := (enw = '1') and (count < 4);
                 do_read := (enr = '1') and (count > 0);

                   if do_write then
                       memory(to_integer(writeptr)) <= datain;
                       if writeptr = "11" then
                           writeptr <= "00";
                       else
                           writeptr <= writeptr + 1;
                       end if;
                   end if;

                   if do_read then
                       dataout <= memory(to_integer(readptr));
                       if readptr = "11" then
                           readptr <= "00";
                       else
                           readptr <= readptr + 1;
                       end if;
                   end if;

                  if do_write and not do_read then
                      count <= count + 1;
                  elsif do_read and not do_write then
                      count <= count - 1;
                  end if;
             end if;
         end if;
     end process;

    empty <= '1' when count = 0 else '0';
    full <= '1' when count = 4 else '0';
end Behavioral;
