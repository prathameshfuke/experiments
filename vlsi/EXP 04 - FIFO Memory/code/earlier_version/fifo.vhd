-- EXP 04 - FIFO memory 8 x 8 (design: fifo.vhd, testbench: fifo_tb.vhd)
--
-- STEPS (Vivado)
--  1. File > Project > New > RTL Project. Tick 'Do not specify sources at this time'.
--     Part: xc7s50csga324-1  (Boolean Board, Spartan-7 XC7S50CSGA324-1)  (or pick the 'Boolean Board' if the board files are installed).
--  2. Add Sources > Add or create design sources > add the design .vhd (and counter_top.vhd for Exp 3).
--     Add Sources > Add or create simulation sources > add the *_tb.vhd.
--  3. In Sources > Simulation Sources, right-click the *_tb > Set as Top.
--  4. Flow Navigator > Simulation > Run Simulation > Run Behavioral Simulation. Run for 300 ns (Run All).
--     View > Zoom Fit. Change radix of buses (right-click signal > Radix) and screenshot the waveform.
--     Tcl console must print the 'PASSED' message.
--  5. RTL Analysis > Open Elaborated Design > Schematic (screenshot).
--  6. Sources > Design Sources: right-click fifo > Set as Top.
--  7. Add Sources > Add or create constraints > add the Boolean Board master XDC (Real Digital).
--     Uncomment the lines for the ports below and rename each port in the XDC to match:
--       clk -> BTN0 (one press = one write/read cycle)
--       reset -> BTN3
--       w -> SW15 ; r -> SW14
--       d[7:0] -> SW7..SW0
--       q[7:0] -> LD7..LD0
--       empty -> LD14 ; full -> LD15
--  8. Synthesis > Run Synthesis, then Implementation > Run Implementation, then Generate Bitstream.
--  9. Board: USB cable to the PROG/UART port, power switch ON.
-- 10. Open Hardware Manager > Open Target > Auto Connect > Program Device > Program.
-- 11. Test with the switches/buttons and watch the LEDs.
--
-- NOTE
--   Set d on the switches, raise w for one clock to write, raise r for one clock to read.

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

-- Synchronous FIFO, 8 locations x 8 bits. w = write, r = read, reset is synchronous.
entity fifo is
    port (
        clk   : in  std_logic;
        reset : in  std_logic;
        w     : in  std_logic;
        r     : in  std_logic;
        d     : in  std_logic_vector(7 downto 0);
        q     : out std_logic_vector(7 downto 0);
        empty : out std_logic;
        full  : out std_logic
    );
end fifo;

architecture Behavioral of fifo is
    type mem_t is array (0 to 7) of std_logic_vector(7 downto 0);
    signal mem    : mem_t := (others => (others => '0'));
    signal wr_ptr : unsigned(2 downto 0) := (others => '0');
    signal rd_ptr : unsigned(2 downto 0) := (others => '0');
    signal count  : unsigned(3 downto 0) := (others => '0');
begin
    process (clk)
        variable do_w, do_r : boolean;
    begin
        if rising_edge(clk) then
            if reset = '1' then
                wr_ptr <= (others => '0');
                rd_ptr <= (others => '0');
                count  <= (others => '0');
                q      <= (others => '0');
            else
                do_w := (w = '1') and (count /= 8);
                do_r := (r = '1') and (count /= 0);
                if do_w then
                    mem(to_integer(wr_ptr)) <= d;
                    wr_ptr <= wr_ptr + 1;
                end if;
                if do_r then
                    q <= mem(to_integer(rd_ptr));
                    rd_ptr <= rd_ptr + 1;
                end if;
                if do_w and not do_r then
                    count <= count + 1;
                elsif do_r and not do_w then
                    count <= count - 1;
                end if;
            end if;
        end if;
    end process;

    empty <= '1' when count = 0 else '0';
    full  <= '1' when count = 8 else '0';
end Behavioral;
