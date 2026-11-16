library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

-- Boolean Board wrapper for Exp 3: 100 MHz clock divided to ~1 Hz so the count is visible on the LEDs.
-- SLOW_BITS = 26 gives 100 MHz / 2^26 = 1.49 Hz. Change it to tune the speed.
entity counter_top is
    generic (SLOW_BITS : positive := 26);
    port (
        clk100 : in  std_logic;                       -- 100 MHz board clock
        sw     : in  std_logic_vector(2 downto 0);    -- sw(0) = rst, sw(1) = en, sw(2) = up
        led    : out std_logic_vector(3 downto 0)     -- LD3..LD0 show Qout
    );
end counter_top;

architecture Behavioral of counter_top is
    signal div  : unsigned(SLOW_BITS - 1 downto 0) := (others => '0');
    signal tick : std_logic;
    signal prev : std_logic := '0';
    signal en_t : std_logic;
begin
    process (clk100)
    begin
        if rising_edge(clk100) then
            div  <= div + 1;
            prev <= div(SLOW_BITS - 1);
        end if;
    end process;
    tick <= div(SLOW_BITS - 1) and not prev;          -- one 100 MHz cycle wide pulse per slow period
    en_t <= sw(1) and tick;

    u : entity work.updown_counter
        port map (clk => clk100, rst => sw(0), en => en_t, up => sw(2), Qout => led);
end Behavioral;
