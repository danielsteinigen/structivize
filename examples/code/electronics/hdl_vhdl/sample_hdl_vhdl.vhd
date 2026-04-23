library ieee;
use ieee.std_logic_1164.all;

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity UpDownCounter is
    Port (
        clk     : in  STD_LOGIC;
        reset_n : in  STD_LOGIC;
        enable  : in  STD_LOGIC;
        up_down : in  STD_LOGIC;
        count   : out STD_LOGIC_VECTOR(3 downto 0)
    );
end UpDownCounter;

architecture Behavioral of UpDownCounter is
    signal cnt_reg : unsigned(3 downto 0) := (others => '0');
begin
    process(clk, reset_n)
    begin
        if reset_n = '0' then
            cnt_reg <= (others => '0');
        elsif rising_edge(clk) then
            if enable = '1' then
                if up_down = '1' then
                    cnt_reg <= cnt_reg + 1;
                else
                    cnt_reg <= cnt_reg - 1;
                end if;
            end if;
        end if;
    end process;
    count <= std_logic_vector(cnt_reg);
end Behavioral;