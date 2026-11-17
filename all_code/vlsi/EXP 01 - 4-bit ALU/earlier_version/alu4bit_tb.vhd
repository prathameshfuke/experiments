library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity alu4bit_tb is
end alu4bit_tb;

architecture sim of alu4bit_tb is
    signal A, B : std_logic_vector(3 downto 0) := (others => '0');
    signal S    : std_logic_vector(2 downto 0) := (others => '0');
    signal Y    : std_logic_vector(3 downto 0);

    type vec is array (0 to 1) of integer;
    constant TA : vec := (10, 5);
    constant TB : vec := (3, 12);

    function expected(a, b, s : integer) return integer is
    begin
        case s is
            when 0 => return (a + b) mod 16;
            when 1 => return (a - b) mod 16;
            when 2 => return to_integer(unsigned(to_unsigned(a, 4) and to_unsigned(b, 4)));
            when 3 => return to_integer(unsigned(to_unsigned(a, 4) or  to_unsigned(b, 4)));
            when 4 => return b;
            when 5 => return to_integer(unsigned(to_unsigned(a, 4) xor to_unsigned(b, 4)));
            when 6 => return (b - a) mod 16;
            when others => return a;
        end case;
    end function;
begin
    uut : entity work.alu4bit port map (A => A, B => B, S => S, Y => Y);

    stim : process
    begin
        for p in vec'range loop
            A <= std_logic_vector(to_unsigned(TA(p), 4));
            B <= std_logic_vector(to_unsigned(TB(p), 4));
            for op in 0 to 7 loop
                S <= std_logic_vector(to_unsigned(op, 3));
                wait for 10 ns;
                assert to_integer(unsigned(Y)) = expected(TA(p), TB(p), op)
                    report "ALU mismatch: A=" & integer'image(TA(p)) & " B=" & integer'image(TB(p)) &
                           " S=" & integer'image(op) & " Y=" & integer'image(to_integer(unsigned(Y)))
                    severity failure;
            end loop;
        end loop;
        report "ALU: all 16 test vectors PASSED";
        wait;
    end process;
end sim;
