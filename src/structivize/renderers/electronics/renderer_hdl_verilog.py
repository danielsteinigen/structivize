from ...renderer import Renderer
from .renderer_hdl_yosys import RendererHdlYosys


@Renderer.register("hdl_verilog")
class RendererHdlVerilog(RendererHdlYosys):
    DEFAULT_TOOL_CONFIGS = {
        "yosys": { "bg_color": "#FFFFFF", "line_color": "#000000", "dff_fill": "#eeaaff", "mux_fill": "#e6e6e6", "gate_fill": "#ffd474", "arith_fill": "#ffc1c1", "io_fill": "#87decd", "text_color": "#000000" },
        "yosys_2": {},
        "yosys_all": {},
        "yosys_detail": {},
        "graphviz": {},
        "graphviz_detail": {},
    }
    FILE_EXT = "v"

    def preprocess_code(self):
        self._code = self._code.strip()

    def _render_yosys(self):
        entity_name = self._get_entity_name(verilog=True)
        command = [
            "yosys",
            "-p",
            f"read_verilog -sv {self._filepath_code}; prep -top {entity_name}; write_json -compat-int {self.filepath_image}.json; stat -json",
        ]
        self._run_command(command=command)

    def _render_yosys_all(self):
        command = [
            "yosys",
            "-p",
            f"read_verilog -sv {self._filepath_code}; proc; opt; write_json -compat-int {self.filepath_image}.json; stat -json",
        ]
        self._run_command(command=command)

    def _render_yosys_2(self):
        entity_name = self._get_entity_name(verilog=True)
        command = [
            "yosys",
            "-p",
            f"read_verilog -sv {self._filepath_code}; hierarchy -top {entity_name}; proc; opt_clean; write_json -compat-int {self.filepath_image}.json; stat -json",
        ]
        self._run_command(command=command)

    def _render_yosys_detail(self):
        entity_name = self._get_entity_name(verilog=True)
        command = [
            "yosys",
            "-p",
            f"read_verilog -sv {self._filepath_code}; prep -top {entity_name}; aigmap; write_json -compat-int {self.filepath_image}.json; stat -json",
        ]
        self._run_command(command=command)

    def _render_graphviz(self):
        command = ["yosys", "-p", f"read_verilog -sv {self._filepath_code}; proc; opt; viz -format svg -prefix {self.filepath_image}"]
        self._execute_process(commands=command)
        self._svg_save(self.filepath_image)

    def _render_graphviz_detail(self):
        command = ["yosys", "-p", f"read_verilog -sv {self._filepath_code}; proc; opt; show -format svg -prefix {self.filepath_image}"]
        self._execute_process(commands=command)
        self._svg_save(self.filepath_image)
