library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity bitcounter_test is
end bitcounter_test;

architecture behavior of bitcounter_test is
    component bitcounter
        Port (
            clk : in std_logic;
            clr : in std_logic;
            q   : out std_logic_vector(3 downto 0)
        );
    end component;

    signal clk : std_logic := '0';
    signal clr : std_logic := '0';
    signal q   : std_logic_vector(3 downto 0);
begin
    uut: bitcounter port map(clk=>clk, clr=>clr, q=>q);

     clock_process : process
     begin
         while true loop
             clk <= '0'; wait for 10 ns;
             clk <= '1'; wait for 10 ns;
         end loop;
     end process;

    stim_proc : process
    begin
        clr <= '1'; wait for 20 ns;
        clr <= '0'; wait for 360 ns;
        wait;
    end process;
end behavior;
