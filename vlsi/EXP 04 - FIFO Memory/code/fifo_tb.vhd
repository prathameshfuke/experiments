library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity fifo_tb is
end fifo_tb;

architecture sim of fifo_tb is
    signal clk, reset, w, r : std_logic := '0';
    signal d, q : std_logic_vector(7 downto 0) := (others => '0');
    signal empty, full : std_logic;
    signal done : boolean := false;
begin
    uut : entity work.fifo port map (clk => clk, reset => reset, w => w, r => r, d => d, q => q, empty => empty, full => full);

    clk <= not clk after 5 ns when not done;

    stim : process
        procedure push(v : integer) is
        begin
            d <= std_logic_vector(to_unsigned(v, 8)); w <= '1';
            wait until rising_edge(clk); wait for 1 ns; w <= '0';
        end procedure;
        procedure pop(exp : integer) is
        begin
            r <= '1'; wait until rising_edge(clk); wait for 1 ns; r <= '0';
            assert to_integer(unsigned(q)) = exp
                report "FIFO read " & integer'image(to_integer(unsigned(q))) & ", expected " & integer'image(exp)
                severity failure;
        end procedure;
    begin
        reset <= '1'; wait for 22 ns; reset <= '0'; wait for 10 ns;
        assert empty = '1' and full = '0' report "FIFO should start empty" severity failure;

        for i in 1 to 8 loop push(16#A0# + i); end loop;     -- fill: A1 .. A8
        assert full = '1' and empty = '0' report "FIFO should be full" severity failure;
        push(16#FF#);                                        -- write while full is ignored
        assert full = '1' report "FIFO overflow" severity failure;

        for i in 1 to 8 loop pop(16#A0# + i); end loop;      -- drain in the same order
        assert empty = '1' and full = '0' report "FIFO should be empty" severity failure;
        r <= '1'; wait until rising_edge(clk); wait for 1 ns; r <= '0';   -- read while empty is ignored
        assert empty = '1' report "FIFO underflow" severity failure;

        push(16#11#); push(16#22#); pop(16#11#); push(16#33#); pop(16#22#); pop(16#33#);
        wait for 20 ns;
        report "FIFO: fill / full / drain / empty / order checks PASSED";
        done <= true;
        wait;
    end process;
end sim;
