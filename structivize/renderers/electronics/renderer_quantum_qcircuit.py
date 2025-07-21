from pylatex import Document, NoEscape, Package

from ...renderer import Renderer
from ...utils import remove_files


@Renderer.register("quantum_qcircuit")
class RendererQuantumQcircuit(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "qcircuit": {},
    }

    def _create_latex(self, tex, filepath):
        pdf_kwargs = {"compiler": "latexmk", "compiler_args": ["-pdfps"]}
        doc = Document(documentclass="article", document_options="dvips")
        doc.packages.append(Package("amsmath"))
        doc.packages.append(Package("qcircuit"))
        doc.preamble.append(Package("inputenc", options=["utf8"]))
        doc.append(NoEscape("\\pagenumbering{gobble}"))
        doc.append(NoEscape(tex))
        doc.generate_pdf(f"{filepath}", **pdf_kwargs)

        self._pdf_save(filepath)
        remove_files(filepath, ["ps", "dvi"])

    def _render_qcircuit(self):
        self._create_latex(self._code, self.filepath_image)