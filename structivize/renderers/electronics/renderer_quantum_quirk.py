import json

import cirq
from cirq.contrib.qcircuit import circuit_to_latex_using_qcircuit
from cirq.contrib.svg import circuit_to_svg

from ...renderer import Renderer
from .renderer_quantum_qcircuit import RendererQuantumQcircuit


@Renderer.register("quantum_quirk")
class RendererQuantumQuirk(RendererQuantumQcircuit):
    DEFAULT_TOOL_CONFIGS = {
        "cirq": {},
    }

    def preprocess_code(self):
        self.clean_code_lines("{")
        self._code = self._code.strip()

    def _render_cirq(self):
        quirk_json = json.loads(self._code)
        qc = cirq.quirk_json_to_circuit(quirk_json)

        tex = circuit_to_latex_using_qcircuit(qc)
        self._create_latex(tex, self.filepath_image)

        # qc_svg = circuit_to_svg(qc)
        # self._svg_save(self.filepath_image, qc_svg)
