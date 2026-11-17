library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity shiftregister is
end shiftregister;

architecture Behavioral of shiftregister is
    component registers
        Port (
            clk : in STD_LOGIC;
            il   : in STD_LOGIC;
            ir   : in STD_LOGIC;
            rst : in STD_LOGIC;
            mode : in STD_LOGIC_VECTOR(1 downto 0);
            i    : in STD_LOGIC_VECTOR(3 downto 0);
            q    : out STD_LOGIC_VECTOR(3 downto 0)
        );
    end component;

    signal clk : STD_LOGIC := '0';
    signal il   : STD_LOGIC := '0';
    signal ir   : STD_LOGIC := '0';
    signal rst : STD_LOGIC := '0';
    signal mode : STD_LOGIC_VECTOR(1 downto 0) := "00";
    signal i    : STD_LOGIC_VECTOR(3 downto 0) := "0000";
    signal q    : STD_LOGIC_VECTOR(3 downto 0);
begin
    uut: registers port map(clk=>clk, il=>il, ir=>ir, rst=>rst, mode=>mode, i=>i, q=>q);

     clk_process : process
     begin
         while true loop
             clk <= '0'; wait for 50 ns;
             clk <= '1'; wait for 50 ns;
         end loop;
     end process;

     stimulus_process : process



begin
         rst <= '1'; wait for 100 ns;
         rst <= '0';

        mode <= "01"; i <= "1010"; wait for 100 ns; -- load
        mode <= "00"; wait for 100 ns;                -- hold
        mode <= "10"; ir <= '1'; wait for 100 ns;     -- left shift
        ir <= '0'; wait for 100 ns;
        mode <= "11"; il <= '1'; wait for 100 ns;     -- right shift
        il <= '0'; wait for 100 ns;
        mode <= "01"; i <= "1100"; wait for 100 ns;
        mode <= "00"; wait for 100 ns;
        rst <= '1'; wait for 100 ns;
        rst <= '0'; wait for 100 ns;
        wait;
    end process;
end Behavioral;
