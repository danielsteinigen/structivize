from ...renderer import Renderer, StatisticResponse
import re
from collections import Counter


@Renderer.register("nn_onnx")
class RendererNnOnnx(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "netron": {},
    }
    FILE_EXT = "onnx"

    def _render_netron(self):
        self._execute_process(commands=["netron_export", "--output", f"{self.filepath_image}.svg", self._filepath_code])
        self._svg_save(self.filepath_image)


    def statistics(self) -> StatisticResponse:
        node_blocks = re.findall(r'\bnode\s*{(.*?)}', self._code, flags=re.DOTALL)
        op_types = Counter()

        for block in node_blocks:
            match = re.search(r'op_type:\s*["\'](.*?)["\']', block)
            if match:
                op_type = match.group(1)
                op_types[op_type] += 1

        return StatisticResponse(node_types={
            'num_nodes': len(node_blocks),
            'op_types': dict(op_types)
        })

