import re

from lcapy import Circuit

from ...renderer import Renderer


@Renderer.register("circuit_lcapy")
class RendererCircuitLcapy(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "lcapy": {},
    }
    FILE_EXT = "net"

    def _convert_units(self, text):
        unit_prefixes = {"p": "e-12", "n": "e-9", "u": "e-6", "m": "e-3", "k": "e+3", "M": "e+6", "G": "e+9"}

        def replacement(match):
            value, prefix, unit = match.groups()
            if unit == "V":  # Remove unit V
                return value
            if prefix in unit_prefixes:
                return f"{value}{unit_prefixes[prefix]}"
            return match.group(0)

        pattern = r"(\d+)([pnumkMG]?)([A-Za-z]*)"
        return re.sub(pattern, replacement, text)

    def preprocess_code(self) -> str:
        code = ""
        for line in self._code.split("\n"):
            if not line.startswith("//") and not line.startswith("```") and not line.startswith("*"):
                code += f"{line}\n"
        code = code.strip()
        self._code = self._convert_units(code)

    def _render_lcapy(self):
        cct = Circuit(
            f"{self._code}\n; autoground=true, style=american, draw_nodes=connections, node_spacing=3, label_style=split, label_ids=true, label_nodes=primary"
        )
        cct.draw(filename=f"{self.filepath_image}.svg")
        self._svg_save(self.filepath_image)

    # https://lcapy.readthedocs.io/en/latest/schematics.html#schtex
    # schtex --draw-nodes=connections --label-nodes=none --cpt-size=1 --help-lines=1 circuit_3_1.txt circuit.png
