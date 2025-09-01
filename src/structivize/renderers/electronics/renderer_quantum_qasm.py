import qiskit.qasm2
import qiskit.qasm3
from cirq.contrib.qasm_import import circuit_from_qasm
from cirq.contrib.qcircuit import circuit_to_latex_using_qcircuit

from ...renderer import Renderer
from .renderer_quantum_qcircuit import RendererQuantumQcircuit


@Renderer.register("quantum_qasm2")
class RendererQuantumQasm2(RendererQuantumQcircuit):
    DEFAULT_TOOL_CONFIGS = {
        "qiskit": {},
        "cirq": {},
    }
    FILE_EXT = "qasm"

    def preprocess_code(self):
        if "include" not in self._code.lower():
            self._code = f'include "qelib1.inc";\n{self._code}'
        if "openqasm" not in self._code.lower():
            self._code = f"OPENQASM 2.0;\n{self._code}"
        self._code = self._code.strip()

    # https://docs.quantum.ibm.com/guides/interoperate-qiskit-qasm2
    def _render_qiskit(self):
        qc = qiskit.qasm2.loads(self._code)
        qc.draw(output="mpl", filename=f"{self.filepath_image}.png")

    def _render_cirq(self):
        qc = circuit_from_qasm(self._code)
        tex = circuit_to_latex_using_qcircuit(qc)
        self._create_latex(tex, self.filepath_image)


@Renderer.register("quantum_qasm3")
class RendererQuantumQasm3(RendererQuantumQcircuit):
    DEFAULT_TOOL_CONFIGS = {
        "qiskit": {},
    }
    FILE_EXT = "qasm"

    # https://docs.quantum.ibm.com/guides/interoperate-qiskit-qasm3
    def _render_qiskit(self):
        qc = qiskit.qasm3.loads(self._code)
        qc.draw(output="mpl", filename=f"{self.filepath_image}.png")
