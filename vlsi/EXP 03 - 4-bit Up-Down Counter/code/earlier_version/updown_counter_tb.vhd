library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity updown_counter_tb is
end updown_counter_tb;

architecture sim of updown_counter_tb is
    signal clk, rst, en, up : std_logic := '0';
    signal Qout : std_logic_vector(3 downto 0);
    signal done : boolean := false;
    signal model : unsigned(3 downto 0) := (others => '0');
begin
    uut : entity work.updown_counter port map (clk => clk, rst => rst, en => en, up => up, Qout => Qout);

    clk <= not clk after 5 ns when not done;

    -- reference model, compared on every falling edge
    process (clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then model <= (others => '0');
            elsif en = '1' then
                if up = '1' then model <= model + 1; else model <= model - 1; end if;
            end if;
        elsif falling_edge(clk) then
            assert unsigned(Qout) = model report "Counter mismatch" severity failure;
        end if;
    end process;

    stim : process
    begin
        rst <= '1'; wait for 22 ns; rst <= '0';
        en <= '1'; up <= '1'; wait for 190 ns;      -- count up through the 15 -> 0 wrap
        up <= '0';            wait for 190 ns;      -- count down through the 0 -> 15 wrap
        en <= '0';            wait for 30 ns;       -- hold
        rst <= '1';           wait for 20 ns;       -- reset
        rst <= '0'; en <= '1'; up <= '1'; wait for 40 ns;
        report "Counter: up / down / hold / reset checks PASSED";
        done <= true;
        wait;
    end process;
end sim;
