import re
from collections import Counter

from ...renderer import Renderer, StatisticResponse


@Renderer.register("nn_onnx")
class RendererNnOnnx(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "netron": {"horizontal": False},
    }
    FILE_EXT = "onnx"

    def _render_netron(self):
        cmd = ["netron_export"]
        if "horizontal" in self.tool_config and self.tool_config["horizontal"]:
            cmd.extend(["--horizontal"])
        
        cmd.extend(["--output", f"{self.filepath_image}.svg", self._filepath_code])
        self._execute_process(commands=cmd)
        self._svg_save(self.filepath_image)

    def statistics(self) -> StatisticResponse:
        node_blocks = re.findall(r"\bnode\s*{(.*?)}", self._code, flags=re.DOTALL)
        op_types = Counter()

        for block in node_blocks:
            match = re.search(r'op_type:\s*["\'](.*?)["\']', block)
            if match:
                op_type = match.group(1)
                op_types[op_type] += 1

        return StatisticResponse(node_types=dict(op_types)) # "num_nodes": len(node_blocks) 
