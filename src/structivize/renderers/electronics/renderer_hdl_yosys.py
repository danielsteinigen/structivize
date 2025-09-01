from ...renderer import Renderer, StatisticResponse
from ...utils import load_text
from collections import defaultdict
import json


@Renderer.register("hdl_yosys")
class RendererHdlYosys(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "netlistsvg": {},
    }
    FILE_EXT = "json"

    def preprocess_code(self):
        self._clean_code_lines("{")
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
            self._svg_save(self.filepath_image)

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


    def statistics(self) -> StatisticResponse:
        gate_map = { # '$add': '', '$mul': '', '$eq': '', '$sub': '', '$mod': 'Modulo', '$gt': '', 
            '$mux': 'Multiplexer', '$not': 'Negation Gates', '$xor': 'XOR Gates', '$or': 'OR gates', '$and': 'AND gates', '$dff': 'Flip-Flops',
            '$adff': 'Flip-Flops', '$logic_and': 'AND gates', '$logic_or': 'OR gates', '$logic_xor': 'XOR gates', '$logic_not': 'Negation gates'
        }
        text = load_text(self._log_files[self._current_tool])
        start = text.find('{')
        if start == -1:
            return StatisticResponse()

        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_str = text[start:i + 1]
                    try:
                        counts = defaultdict(int)
                        json_stat = json.loads(json_str)
                        module_stat = json_stat["modules"][list(json_stat["modules"].keys())[0]]
                        # counts["ports"] = module_stat["num_ports"]
                        for gate, cnt in module_stat["num_cells_by_type"].items():
                            if gate in gate_map:
                                gate_ = gate_map[gate]
                                counts[gate_] = cnt
                        return StatisticResponse(node_types=dict(counts))
                    except json.JSONDecodeError as e:
                        return StatisticResponse()
        
        return StatisticResponse()
