import os
import shutil

from pylatex import Command, Document, NoEscape, Package

from ...renderer import Renderer
from ...utils import remove_files


@Renderer.register("tikz")
class RendererTikz(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "pylatex": {},
    }
    FILE_EXT = "tikz"

    def _clean_tikz(self, code_raw):
        code = ""
        for line in code_raw.split("\n"):
            line_str = line.strip()
            if (
                not line_str.startswith(r"\documentclass")
                and not line_str.startswith(r"\usepackage")
                and not line_str.startswith(r"\begin{document}")
                and not line_str.startswith(r"\end{document}")
                and not line_str.startswith(r"\usetikzlibrary")
                and not line_str.startswith(r"\document")
                and not line_str.startswith(r"\begin{ladder")
                and not line_str.startswith(r"\end{ladder")
                and not line_str.startswith(r"\ctikzset")
            ):
                code += f"{line}\n"
        return code.strip()

    def _replace_tikz(self, code_raw, search, replace):
        code = ""
        for line in code_raw.split("\n"):
            line_str = line.strip()
            if not line_str.startswith(search):
                code += f"{line}\n"
            else:
                code += f"{replace}\n"
        return code.strip()

    def _insert_begin_end(self, code_raw, search, insert_begin, insert_end):
        code = code_raw
        has_begin = False
        for line in code_raw.split("\n"):
            if line.strip().startswith(search):
                has_begin = True
        if not has_begin:
            code = f"{insert_begin}\n{code_raw}\n{insert_end}"
        return code.strip()

    def _check_library_exists(self):
        libraries = [
            "pgflibraryshapes.gates.pid.code.tex",
            "pgflibraryshapes.gates.pid.ISO14617.code.tex",
            "tikzlibrarycircuits.pid.code.tex",
            "tikzlibrarycircuits.pid.ISO14617.code.tex",
        ]
        for lib in libraries:
            if not os.path.isfile(f"{os.path.dirname(self.filepath_image)}/{lib}"):
                shutil.copyfile(
                    f"{self._tool_path}/tikz/{lib}",
                    f"{os.path.dirname(self.filepath_image)}/{lib}",
                )

    def _create_doc(self):
        pdf_kwargs = {"compiler": "latexmk", "compiler_args": ["-pdfps"]}
        doc = Document(documentclass="article", document_options="dvips")
        doc.packages.append(Package("tikz"))
        return doc, pdf_kwargs

    def preprocess_code(self):
        self._clean_code_lines("\\")
        self._code = self._clean_tikz(self._code.strip())

    def _render_pylatex(self):
        doc, pdf_kwargs = self._create_doc()
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
