library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Added testbench (not in the faculty PDF): presses keys 5, B and 0 on a modelled 4x4 keypad.
-- Row n is selected when a(n) = '0'; a pressed key pulls its column low (b(c) = '0').
entity matrix_key_tb is
end matrix_key_tb;

architecture sim of matrix_key_tb is
    signal clk : std_logic := '0';
    signal a   : std_logic_vector(3 downto 0);
    signal b   : std_logic_vector(3 downto 0) := "1111";
    signal led : std_logic_vector(7 downto 0);
    signal key_row : integer := -1;          -- row of the pressed key, -1 = none (rows numbered 1..4 as in the code)
    signal key_col : std_logic_vector(3 downto 0) := "1111";
    signal done : boolean := false;
begin
    uut : entity work.matrix_key port map (clk => clk, b => b, a => a, led => led);
    clk <= not clk after 5 ns when not done;

    -- key matrix model: row 1 = a "0111", row 2 = "1011", row 3 = "1101", row 4 = "1110"
    process (a, key_row, key_col)
    begin
        b <= "1111";
        if (key_row = 1 and a = "0111") or (key_row = 2 and a = "1011") or
           (key_row = 3 and a = "1101") or (key_row = 4 and a = "1110") then
            b <= key_col;
        end if;
    end process;

    stim : process
        procedure press(r : integer; c : std_logic_vector(3 downto 0); exp : std_logic_vector(7 downto 0); name : string) is
        begin
            key_row <= r; key_col <= c;
            wait for 25 us;                 -- longer than one full scan (8 x 256 clocks = 20.5 us)
            assert led = exp report "Keypad key " & name & ": wrong LED pattern" severity failure;
            key_row <= -1; key_col <= "1111";
            wait for 25 us;
        end procedure;
    begin
        wait for 100 ns;
        press(2, "1101", "01010101", "5");  -- faculty table: row 2, b = 1101 -> 5
        press(3, "0111", "10111011", "B");  -- row 3, b = 0111 -> B
        press(1, "1110", "00000000", "0");  -- row 1, b = 1110 -> 0
        report "Keypad: keys 5, B, 0 matched the faculty LED table PASSED";
        done <= true;
        wait;
    end process;
end sim;
