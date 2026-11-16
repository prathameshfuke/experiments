library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ALU_4_test is
end ALU_4_test;

architecture behavior of ALU_4_test is
    component ALU_4
        Port (
            a   : in std_logic_vector(3 downto 0);
            b   : in std_logic_vector(3 downto 0);
            sel : in std_logic_vector(2 downto 0);
            y   : out std_logic_vector(3 downto 0)
        );
    end component;

    signal a   : std_logic_vector(3 downto 0) := (others => '0');
    signal b   : std_logic_vector(3 downto 0) := (others => '0');
    signal sel : std_logic_vector(2 downto 0) := (others => '0');
    signal y   : std_logic_vector(3 downto 0);
begin
    uut: ALU_4 port map (a => a, b => b, sel => sel, y => y);

     process
     begin
         a <= "1100";
         b <= "0011";
         wait for 100 ns;

          sel <= "000"; wait for 100 ns; -- ADD
          sel <= "001"; wait for 100 ns; -- SUBTRACT
          sel <= "010"; wait for 100 ns; -- AND
          sel <= "011"; wait for 100 ns; -- NAND
          sel <= "100"; wait for 100 ns; -- XOR
          sel <= "101"; wait for 100 ns; -- XNOR
          sel <= "110"; wait for 100 ns; -- OR
          sel <= "111"; wait for 100 ns; -- default

        wait;
    end process;
end behavior;
