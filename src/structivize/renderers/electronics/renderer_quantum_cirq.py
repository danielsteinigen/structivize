import cirq
from cirq.contrib.qcircuit import circuit_to_latex_using_qcircuit
from cirq.contrib.svg import circuit_to_svg

from ...renderer import Renderer
from .renderer_quantum_qcircuit import RendererQuantumQcircuit


@Renderer.register("quantum_cirq")
class RendererQuantumCirq(RendererQuantumQcircuit):
    DEFAULT_TOOL_CONFIGS = {
        "cirq": {},
    }

    # https://quantumai.google/cirq/build/interop
    def _render_cirq(self):
        qc = cirq.read_json(json_text=self._code)
        qc_svg = circuit_to_svg(qc)
        self._svg_save(self.filepath_image, qc_svg)

        # tex = circuit_to_latex_using_qcircuit(qc)
        # self._create_latex(tex, self.filepath_image)
