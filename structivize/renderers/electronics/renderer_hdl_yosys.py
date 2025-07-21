from ...renderer import Renderer
from ...utils import load_text


@Renderer.register("hdl_yosys")
class RendererHdlYosys(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "netlistsvg": {},
    }

    def preprocess_code(self):
        self.clean_code_lines("{")
        self._code = self._code.strip()

    def _conv_netlist2svg(self, filepath_code, filepath_img, analog=False):
        if analog:
            self._execute_process(
                commands=[
                    "netlistsvg",
                    filepath_code,
                    "-o",
                    f"{filepath_img}.svg",
                    "--skin",
                    f"{self._tool_path}/netlistsvg/lib/analog.svg",
                ]
            )
        else:
            self._execute_process(
                commands=[
                    "netlistsvg",
                    filepath_code,
                    "-o",
                    f"{filepath_img}.svg",
                    "--skin",
                    f"{self._tool_path}/netlistsvg/lib/default.svg",
                ]
            )

    def _run_command(self, command):
        self._execute_process(commands=command)
        if "port_directions" in load_text(f"{self.filepath_image}.json"):
            self._conv_netlist2svg(f"{self.filepath_image}.json", f"{self.filepath_image}")
            self._svg_save(self._filepath_image)

    def _get_entity_name(self, verilog: bool = False):
        searchword = "entity" if not verilog else "module"
        lines = self._code.splitlines()

        for line in lines:
            if searchword in line:
                words = line.split()
                entity_index = words.index(searchword)
                return words[entity_index + 1].split("(")[0]
        return None

    def _render_netlistsvg(self):

        if "port_directions" in self._code:
            self._conv_netlist2svg(self._filepath_code, self.filepath_image)

        self._svg_save(self.filepath_image)
