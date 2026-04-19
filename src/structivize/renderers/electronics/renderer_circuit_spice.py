import re
from collections import defaultdict

from ...renderer import NodeType, Renderer, StatisticResponse
from .utils.spice2yosys import convert_spice_to_yosys_json


@Renderer.register("circuit_spice")
class RendererCircuitSpice(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "netlistsvg": {"bg_color": "#FFFFFF", "line_color": "#000000", "text_color": "#000000", "line_width": 1},
    }
    FILE_EXT = "net"

    def verify_code(self):
        success = True
        part = ""
        lines = self._code.strip().splitlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith(("*", ".", ";")):
                tokens = re.split(r"\s+", line)
                part_type = tokens[0][0].upper()
                if part_type not in {"R", "C", "L", "D", "Q", "M", "V", "I"}:  # "S"
                    success = False
                    part += f", {part_type}"
                if (
                    len(tokens[0]) > 6
                    or tokens[0].lower().startswith("lamp")
                    or tokens[0].lower().startswith("led")
                    or tokens[0].lower().startswith("fuse")
                    or tokens[0].lower().startswith("xor")
                ):
                    success = False
                    part += f", {tokens[0]}"

        if not success:
            self.log["log"] += f"# Unknown components found: {part}"
            print(f"Unknown components found: {part}")

        return success

    def _conv_netlist2svg(self, filepath_code, filepath_img):
        self._execute_process(
            commands=["netlistsvg", filepath_code, "-o", f"{filepath_img}.svg", "--skin", f"{self._tool_path}/netlistsvg/lib/analog.svg"]
        )
        with open(f"{filepath_img}.svg", "r") as f:
            content = f.read()

        bg_color = self.tool_config.get("bg_color", "#FFFFFF")
        line_color = self.tool_config.get("line_color", "#000000")
        text_color = self.tool_config.get("text_color", "#000000")
        width = self.tool_config.get("line_width", 1)

        bg_rect = f'<rect id="bg-canvas" width="100%" height="100%" fill="{bg_color}" x="0" y="0"/>'
        content = re.sub(r"(<svg[^>]*>)", lambda m: f"{m.group(1)}\n{bg_rect}", content, count=1)
        css = f"""
        <style>
            path, line, rect, circle, polyline, polygon {{
                stroke: {line_color} !important;
                stroke-width: {width}px !important;
                fill-opacity: 0; /* Ensures components don't have random fills */
            }}
            text {{ 
                fill: {text_color} !important; 
                font-family: monospace; 
                fill-opacity: 1 !important; /* Force text to be visible */
                stroke: none !important;    /* Ensure text doesn't have an outline */
            }}
            .symbol path {{ fill: none; }} 
            #bg-canvas {{
                stroke: none !important;
                stroke-width: 0 !important;
                fill: {bg_color} !important;
                fill-opacity: 1 !important;
            }}
        </style>
        """

        if "</svg>" in content:
            content = content.replace("</svg>", f"{css}\n</svg>")

        with open(f"{filepath_img}.svg", "w") as f:
            content = f.write(content)

    def _render_netlistsvg(self):
        # convert Spice to Yosys and draw with netlistsvg
        convert_spice_to_yosys_json(self._filepath_code, f"{self.filepath_image}.json")
        self._conv_netlist2svg(filepath_code=f"{self.filepath_image}.json", filepath_img=self.filepath_image)
        self._svg_save(self.filepath_image, cropping=False)

    def statistics(self) -> StatisticResponse:
        component_map = {
            "R": "resistors",
            "C": "capacitors",
            "L": "inductors",
            "S": "switches",
            "D": "diodes",
            "V": "voltage sources",
            "I": "current sources",
            "Q": "transistors",
            "M": "transistors",
        }
        counts = defaultdict(int)
        lines = self._code.strip().splitlines()
        for line in lines:
            line = line.strip()
            if line and line[0].isupper():
                component_type = line[0]
                if component_type in component_map:
                    component = component_map[component_type]
                    counts[component] += 1
        return StatisticResponse(node_types=[NodeType(type=name, count=count) for name, count in counts.items()])
