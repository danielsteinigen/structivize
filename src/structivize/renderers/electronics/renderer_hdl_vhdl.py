import os

from graphviz import Source

from ...renderer import Renderer
from ...utils import remove_files_dir
from .renderer_hdl_yosys import RendererHdlYosys


@Renderer.register("hdl_vhdl")
class RendererHdlVhdl(RendererHdlYosys):
    DEFAULT_TOOL_CONFIGS = {
        "yosys": {},
        "yosys_2": {},
        "yosys_all": {},
        "yosys_detail": {},
        "graphviz": {},
        "graphviz_detail": {},
        "graphviz_ast": {},
    }

    def preprocess_code(self):
        self._code = self._code.strip()
        self._code = (
            self._code.replace("use IEEE.STD_LOGIC;", "use IEEE.STD_LOGIC_1164.ALL;")
            .replace("use IEEE.STD_LOGIC_ARITH;", "use IEEE.STD_LOGIC_ARITH.ALL;")
            .replace("use IEEE.STD_LOGIC_UNSIGNED;", "use IEEE.STD_LOGIC_UNSIGNED.ALL;")
            .replace("use IEEE.STD_LOGIC_SIGNED;", "use IEEE.STD_LOGIC_SIGNED.ALL;")
            .replace("use IEEE.NUMERIC_STD;", "use IEEE.NUMERIC_STD.ALL;")
        )
        self._code = (
            self._code.replace("use ieee.std_logic;", "use ieee.std_logic_1164.all;")
            .replace("use ieee.std_logic_arith;", "use ieee.std_logic_arith.all;")
            .replace("use ieee.std_logic_unsigned;", "use ieee.std_logic_unsigned.all;")
            .replace("use ieee.std_logic_signed;", "use ieee.std_logic_signed.all;")
            .replace("use ieee.numeric_std;", "use ieee.numeric_std.all;")
        )
        if "STD_LOGIC" in self._code and "use IEEE.STD_LOGIC" not in self._code:
            self._code = f"use IEEE.STD_LOGIC_1164.ALL;\n\n{self._code}"
            if "library IEEE;" not in self._code:
                self._code = f"library IEEE;\n{self._code}"
        if "std_logic" in self._code and "use ieee.std_logic" not in self._code:
            self._code = f"use ieee.std_logic_1164.all;\n\n{self._code}"
            if "library ieee;" not in self._code:
                self._code = f"library ieee;\n{self._code}"

    def _render_yosys(self):
        entity_name = self._get_entity_name()
        for std in ["08", "19", "93", "87"]:
            command_0 = ["ghdl", "-a", f"--std={std}", "--ieee=standard", "-fsynopsys", self._filepath_code]
            command_1 = [
                "yosys",
                "-m",
                "ghdl",
                "-p",
                f"ghdl --std={std} --ieee=standard -fsynopsys {entity_name}; prep -top {entity_name}; write_json -compat-int {self.filepath_image}.json; stat -json",
            ]
            self._execute_process(commands=command_0)
            self._run_command(command=command_1)
            break
        remove_files_dir(os.getcwd(), ["o", "cf"])

    def _render_yosys_2(self):
        entity_name = self._get_entity_name()
        for std in ["08", "19", "93", "87"]:
            # command_0 = ["ghdl", "-a", f"--std={std}", "--ieee=standard" ,"-fsynopsys", self._filepath_code]
            command_1 = [
                "yosys",
                "-m",
                "ghdl",
                "-p",
                f"ghdl --std={std} --ieee=standard -fsynopsys {entity_name}; prep -top {entity_name} -flatten; write_json -compat-int {self.filepath_image}.json; stat -json",
            ]
            # self._execute_process(commands=command_0)
            self._run_command(command=command_1)
            break
        remove_files_dir(os.getcwd(), ["o", "cf"])

    def _render_yosys_all(self):
        for std in ["08", "19", "93", "87"]:
            # command_0 = ["ghdl", "-a", f"--std={std}", "--ieee=standard" ,"-fsynopsys", self._filepath_code]
            command_1 = [
                "yosys",
                "-m",
                "ghdl",
                "-p",
                f"ghdl --std={std} --ieee=standard -fsynopsys {self._filepath_code} -e; proc; opt; write_json -compat-int {self.filepath_image}.json; stat -json",
            ]
            # self._execute_process(commands=command_0)
            self._run_command(command=command_1)
            break
        remove_files_dir(os.getcwd(), ["o", "cf"])

    def _render_yosys_detail(self):
        entity_name = self._get_entity_name()
        for std in ["08", "19", "93", "87"]:
            command_0 = ["ghdl", "-a", f"--std={std}", "--ieee=standard", "-fsynopsys", self._filepath_code]
            command_1 = [
                "yosys",
                "-m",
                "ghdl",
                "-p",
                f"ghdl --std={std} --ieee=standard -fsynopsys {entity_name}; prep -top {entity_name}; aigmap; write_json -compat-int {self.filepath_image}.json; stat -json",
            ]
            self._execute_process(commands=command_0)
            self._run_command(command=command_1)
        remove_files_dir(os.getcwd(), ["o", "cf"])

    def _render_graphviz(self):
        for std in ["08", "19", "93", "87"]:
            command = [
                "yosys",
                "-m",
                "ghdl",
                "-p",
                f"ghdl --std={std} --ieee=standard -fsynopsys {self._filepath_code} -e; proc; opt; viz -format svg -prefix {self.filepath_image}",
            ]
            self._execute_process(commands=command)
            self._svg_save(self._filepath_image)
            break

    def _render_graphviz_detail(self):
        for std in ["08", "19", "93", "87"]:
            command = [
                "yosys",
                "-m",
                "ghdl",
                "-p",
                f"ghdl --std={std} --ieee=standard -fsynopsys {self._filepath_code} -e; proc; opt; show -format svg -prefix {self.filepath_image}",
            ]
            self._execute_process(commands=command)
            self._svg_save(self._filepath_image)
            break

    def _render_graphviz_ast(self):
        # AST - Abstract Syntax Tree
        entity_name = self._get_entity_name()
        for std in ["08", "19", "93", "87"]:
            command = ["ghdl", "--synth", f"--std={std}", "--ieee=standard", "-fsynopsys", "--out=dot", entity_name]
            _, out, _ = self._execute_process(commands=command)
            # save_text(filename=f"{self.filepath_image}.dot", data=out)
            src = Source(out)
            src.render(self.filepath_image, format="png", view=False)
            break
        remove_files_dir(os.getcwd(), ["o", "cf"])
