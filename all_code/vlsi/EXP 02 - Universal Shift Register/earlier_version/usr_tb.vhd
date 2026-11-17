library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity usr_tb is
end usr_tb;

architecture sim of usr_tb is
    signal clk : std_logic := '0';
    signal S   : std_logic_vector(1 downto 0) := "00";
    signal IL, IR : std_logic := '0';
    signal P   : std_logic_vector(3 downto 0) := "0000";
    signal Q   : std_logic_vector(3 downto 0);
    signal done : boolean := false;

    procedure chk(signal q : in std_logic_vector(3 downto 0); exp : std_logic_vector(3 downto 0); msg : string) is
    begin
        assert q = exp report "USR " & msg & " failed" severity failure;
    end procedure;
begin
    uut : entity work.usr port map (clk => clk, S => S, IL => IL, IR => IR, P => P, Q => Q);

    clk <= not clk after 5 ns when not done;

    stim : process
    begin
        -- PIPO: parallel in, parallel out
        S <= "00"; P <= "1010"; wait until rising_edge(clk); wait for 1 ns;
        chk(Q, "1010", "PIPO load");
        -- SIPO: shift right 4 bits serially (IL = 1,1,0,0), read Q in parallel
        S <= "01"; IL <= '1'; wait until rising_edge(clk); wait for 1 ns;
        IL <= '1'; wait until rising_edge(clk); wait for 1 ns;
        IL <= '0'; wait until rising_edge(clk); wait for 1 ns;
        IL <= '0'; wait until rising_edge(clk); wait for 1 ns;
        chk(Q, "0011", "SIPO shift right");
        -- hold
        S <= "11"; wait until rising_edge(clk); wait for 1 ns;
        chk(Q, "0011", "hold");
        -- shift left with IR = 1 (serial in, left)
        S <= "10"; IR <= '1'; wait until rising_edge(clk); wait for 1 ns;
        chk(Q, "0111", "shift left");
        -- PISO: load 1101, shift right and watch Q(0) as serial out
        S <= "00"; P <= "1101"; wait until rising_edge(clk); wait for 1 ns;
        S <= "01"; IL <= '0';
        wait until rising_edge(clk); wait for 1 ns; chk(Q, "0110", "PISO 1");
        wait until rising_edge(clk); wait for 1 ns; chk(Q, "0011", "PISO 2");
        wait until rising_edge(clk); wait for 1 ns; chk(Q, "0001", "PISO 3");
        wait until rising_edge(clk); wait for 1 ns; chk(Q, "0000", "PISO 4");
        -- SISO: one bit in, appears at the other end after 4 clocks
        S <= "01"; IL <= '1'; wait until rising_edge(clk); wait for 1 ns;
        IL <= '0';
        for i in 1 to 3 loop
            wait until rising_edge(clk); wait for 1 ns;
        end loop;
        chk(Q, "0001", "SISO bit at serial out");
        wait until rising_edge(clk); wait for 1 ns;
        chk(Q, "0000", "SISO bit gone");
        report "USR: PIPO / SIPO / PISO / SISO checks PASSED";
        done <= true;
        wait;
    end process;
end sim;
