from pylatex import NoEscape, Package

from ...renderer import Renderer
from ...utils import remove_files
from .renderer_tikz import RendererTikz


@Renderer.register("tikz_circuit")
class RendererTikzCircuit(RendererTikz):
    DEFAULT_TOOL_CONFIGS = {
        "circuitikz_eu": {"options": ["europeanresistors", "americaninductors", "europeancurrents", "europeanvoltages"]},
        "circuitikz_us": {"options": ["americanresistors", "cuteinductors", "americancurrents", "europeanvoltages"]},
    }
    FILE_EXT = "tikz"

    def _render_circuitikz(self):
        doc, pdf_kwargs = self._create_doc()
        doc.preamble.append(Package("circuitikz", options=self.tool_config["options"]))
        doc.append(NoEscape("\\pagenumbering{gobble}"))
        doc.append(NoEscape(self._code))
        doc.generate_pdf(f"{self.filepath_image}", **pdf_kwargs)
        self._pdf_save(self.filepath_image)
        remove_files(self.filepath_image, ["ps", "dvi"])

    def _render_circuitikz_eu(self):
        self._render_circuitikz()

    def _render_circuitikz_us(self):
        self._render_circuitikz()
