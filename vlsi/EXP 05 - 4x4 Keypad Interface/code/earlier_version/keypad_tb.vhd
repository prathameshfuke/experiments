library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity keypad_tb is
end keypad_tb;

architecture sim of keypad_tb is
    constant DIV : positive := 4;
    signal clk : std_logic := '0';
    signal row, col : std_logic_vector(3 downto 0);
    signal led : std_logic_vector(15 downto 0);
    signal hex : std_logic_vector(3 downto 0);
    signal pressed : integer := -1;       -- key held down by the "user", -1 = none
    signal done : boolean := false;
begin
    uut : entity work.keypad generic map (SCAN_DIV => DIV)
        port map (clk => clk, row => row, col => col, led => led, hex => hex);

    clk <= not clk after 5 ns when not done;

    -- keypad model: key n connects row n/4 to column n mod 4
    process (row, pressed)
    begin
        col <= "1111";
        if pressed >= 0 then
            if row(pressed / 4) = '0' then
                col(pressed mod 4) <= '0';
            end if;
        end if;
    end process;

    stim : process
        procedure press(n : integer) is
            variable exp : std_logic_vector(15 downto 0) := (others => '0');
        begin
            pressed <= n;
            wait for 16 * DIV * 10 ns;         -- long enough for two full scans
            pressed <= -1;
            wait for 8 * DIV * 10 ns;
            exp(n) := '1';
            assert led = exp report "Keypad: wrong LED for key " & integer'image(n) severity failure;
            assert to_integer(unsigned(hex)) = n report "Keypad: wrong hex for key " & integer'image(n) severity failure;
        end procedure;
    begin
        wait for 20 ns;
        press(0); press(5); press(11); press(15); press(7);   -- 11 = SW11 (LED 11), as in the manual example
        report "Keypad: key 0, 5, 11, 15, 7 detected correctly PASSED";
        done <= true;
        wait;
    end process;
end sim;
