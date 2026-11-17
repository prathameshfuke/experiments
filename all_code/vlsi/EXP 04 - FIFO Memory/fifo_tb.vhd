library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity fifo_tb is
end fifo_tb;

architecture Behavioral of fifo_tb is


component fifo
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
     end component;

    signal clk     : std_logic := '0';
    signal rst     : std_logic := '0';
    signal enw     : std_logic := '0';
    signal enr     : std_logic := '0';
    signal datain : std_logic_vector(3 downto 0) := "0000";
    signal dataout : std_logic_vector(3 downto 0);
    signal empty   : std_logic;
    signal full    : std_logic;
begin
    uut: fifo port map(clk=>clk, rst=>rst, enw=>enw, enr=>enr, datain=>datain, dataout=>dataout, empty=>empty, full=>full);

     clk_process : process
     begin
         while true loop
             clk <= '0'; wait for 50 ns;
             clk <= '1'; wait for 50 ns;
         end loop;
     end process;

     stimulus : process
     begin
         rst <= '1'; wait for 100 ns; rst <= '0'; wait for 100 ns;

          enw <= '1';
          datain <= "0001"; wait for 100 ns;
          datain <= "0010"; wait for 100 ns;
          datain <= "0011"; wait for 100 ns;
          datain <= "0100"; wait for 100 ns;
          enw <= '0'; wait for 100 ns;

          enr <= '1';
          wait for 100 ns; -- 0001
          wait for 100 ns; -- 0010
          wait for 100 ns; -- 0011
          wait for 100 ns; -- 0100
          enr <= '0'; wait for 100 ns;

          -- Simultaneous write/read test
          datain <= "1010"; enw <= '1'; wait for 100 ns;
          enw <= '0'; enr <= '1'; wait for 100 ns;
          enr <= '0';

        report "FIFO TEST COMPLETED";
        wait;
    end process;
end Behavioral;
