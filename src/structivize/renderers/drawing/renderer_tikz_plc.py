from pylatex import Command, NoEscape

from ...renderer import Renderer
from ...utils import remove_files
from .renderer_tikz import RendererTikz


@Renderer.register("tikz_plc")
class RendererTikzPlc(RendererTikz):
    DEFAULT_TOOL_CONFIGS = {
        "pylatex": {},
    }

    def preprocess_code(self):
        self._clean_code_lines("\\")
        self._code = self._clean_tikz(self._code.strip())
        self._code = self._replace_tikz(self._code, r"\begin{tikzpicture}", r"\begin{tikzpicture}[circuit plc ladder,thick]")
        self._code = self._replace_tikz(self._code, r"\begin{circuitikz}", r"\begin{tikzpicture}[circuit plc ladder,thick]")
        self._code = self._replace_tikz(self._code, r"\end{circuitikz}", r"\end{tikzpicture}")
        self._code = self._insert_begin_end(
            self._code, r"\begin{tikzpicture", r"\begin{tikzpicture}[circuit plc ladder,thick]", r"\end{tikzpicture}"
        )

    def _render_pylatex(self):
        doc, pdf_kwargs = self._create_doc()
        doc.preamble.append(Command("usetikzlibrary", "circuits"))
        doc.preamble.append(Command("usetikzlibrary", "circuits.plc.ladder"))
        doc.preamble.append(
            Command(
                "usetikzlibrary",
                "arrows, positioning, shapes, shapes.geometric, shapes.symbols, patterns, automata, backgrounds, petri, calc",
            )
        )
        doc.append(NoEscape("\\pagenumbering{gobble}"))
        doc.append(NoEscape(self._code))
        doc.generate_pdf(f"{self.filepath_image}", **pdf_kwargs)
        self._pdf_save(self.filepath_image)
        remove_files(self.filepath_image, ["ps", "dvi"])
