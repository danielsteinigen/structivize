import json
import re
from collections import defaultdict

from ...renderer import NodeType, Renderer, StatisticResponse
from ...utils import load_text


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

            bg_color = self.tool_config.get("bg_color", "#FFFFFF")
            line_color = self.tool_config.get("line_color", "#000000")
            text_color = self.tool_config.get("text_color", "#000000")
            width = self.tool_config.get("line_width", 1)

            fill_map = {
                "dff": self.tool_config.get("dff_fill", "none"),
                "mux": self.tool_config.get("mux_fill", "none"),
                "gate": self.tool_config.get("gate_fill", "none"),
                "arith": self.tool_config.get("arith_fill", "none"),
                "io": self.tool_config.get("io_fill", "none"),
            }

            def get_fill_for_type(stype):
                stype = stype.lower()

                if any(
                    x in stype
                    for x in [
                        "dff",
                        "adff",
                        "latch",
                        "dff-bus",
                        "dffn",
                        "dffn-bus",
                        "dlatch",
                        "dlatch-bus",
                        "dlatchn",
                        "dlatchn-bus",
                        "generic",
                    ]
                ):
                    return fill_map["dff"]
                if any(x in stype for x in ["mux", "mux-bus"]):
                    return fill_map["mux"]
                if any(
                    x in stype
                    for x in [
                        "and",
                        "or",
                        "not",
                        "xor",
                        "nand",
                        "nor",
                        "andnot",
                        "reduce_nor",
                        "ornot",
                        "reduce_xor",
                        "reduce_nxor",
                        "tribuf",
                        "buf",
                        "_OAI4_",
                        "_AOI4_",
                        "_OAI3_",
                        "_AOI3_",
                    ]
                ):
                    return fill_map["gate"]
                if any(
                    x in stype
                    for x in [
                        "add",
                        "sub",
                        "mul",
                        "div",
                        "eq",
                        "lt",
                        "gt",
                        "le",
                        "ge",
                        "mod",
                        "neg",
                        "pos",
                        "pow",
                        "ne",
                        "shr",
                        "shl",
                        "sshr",
                        "sshl",
                    ]
                ):
                    return fill_map["arith"]
                if any(x in stype for x in ["input", "output", "constant", "inputExt", "outputExt"]):
                    return fill_map["io"]
                return "none"

            with open(f"{filepath_img}.svg", "r") as f:
                content = f.read()

            def style_injector(match):
                full_tag = match.group(1)
                stype_val = match.group(2)
                color = get_fill_for_type(stype_val)
                new_style = f' style="fill: {color}; fill-opacity: 1;"'
                return full_tag.replace(">", f"{new_style}>")

            pattern = r'(<g[^>]*s:type="([^"]+)"[^>]*>)'
            content = re.sub(pattern, style_injector, content)

            css_rules = f"""
                text {{ 
                    fill: {text_color} !important; 
                    font-family: "Courier New", monospace; 
                    font-weight: bold; 
                    stroke: none;
                }}
                /* Global Lines */
                path, rect, circle, line, polygon {{
                    stroke: {line_color};
                    stroke-width: {width}px;
                    stroke-linecap: round;
                }}
                /* Wires (prevent filling) */
                .edge path, svg > line {{ 
                    fill: none !important; 
                }}
                /* Background ID Style */
                #bg-canvas {{
                    stroke: none !important;
                    fill: {bg_color};
                }}
            """

            bg_rect = f'<rect id="bg-canvas" width="100%" height="100%" fill="{bg_color}" x="0" y="0"/>'
            content = re.sub(r"(<svg[^>]*>)", lambda m: f"{m.group(1)}\n{bg_rect}", content, count=1)

            style_block = f"<style>{css_rules}</style>"
            if "</svg>" in content:
                content = content.replace("</svg>", f"{style_block}\n</svg>")

            with open(f"{filepath_img}.svg", "w") as f:
                f.write(content)

    def _run_command(self, command):
        self._execute_process(commands=command)
        if "port_directions" in load_text(f"{self.filepath_image}.json"):
            self._conv_netlist2svg(f"{self.filepath_image}.json", f"{self.filepath_image}")
            self._svg_save(self.filepath_image, cropping=False)

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
        gate_map = {  # '$add': '', '$mul': '', '$eq': '', '$sub': '', '$mod': 'Modulo', '$gt': '',
            "$mux": "Multiplexer",
            "$not": "Negation Gates",
            "$xor": "XOR Gates",
            "$or": "OR gates",
            "$and": "AND gates",
            "$dff": "Flip-Flops",
            "$adff": "Flip-Flops",
            "$logic_and": "AND gates",
            "$logic_or": "OR gates",
            "$logic_xor": "XOR gates",
            "$logic_not": "Negation gates",
            "$_NOT_": "Negation Gates",
            "$_XOR_": "XOR Gates",
            "$_OR_": "OR gates",
            "$_AND_": "AND gates",
        }
        text = self._logs[self._current_tool]["cli"]
        start = text.find("{")
        if start == -1:
            return StatisticResponse()

        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    json_str = text[start : i + 1]
                    try:
                        counts = defaultdict(int)
                        json_stat = json.loads(json_str)
                        module_stat = json_stat["modules"][list(json_stat["modules"].keys())[0]]
                        # counts["ports"] = module_stat["num_ports"]
                        for gate, cnt in module_stat["num_cells_by_type"].items():
                            if gate in gate_map:
                                gate_ = gate_map[gate]
                                counts[gate_] = cnt
                        return StatisticResponse(node_types=[NodeType(type=name, count=count) for name, count in counts.items()])
                    except json.JSONDecodeError as e:
                        return StatisticResponse()

        return StatisticResponse()
