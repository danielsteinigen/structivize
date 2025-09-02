from ...renderer import Renderer


@Renderer.register("state_scxml")
class RendererStateScxml(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "smcat": {},
        "smcat_dot": {},
    }
    FILE_EXT = "xml"

    def preprocess_code(self):
        self._clean_code_lines("<")
        self._code = self._code.strip()
        if not self._code.startswith("<?xml"):
            self._code = f'<?xml version="1.0" encoding="UTF-8"?>\n{self._code}'

    def _render_smcat(self):
        # uses circo engine instead of dot
        self._execute_process(
            commands=["smcat", "-T", "svg", "-I", "scxml", "-E", "circo", self._filepath_code, "-o", f"{self.filepath_image}.svg"]
        )
        self._svg_save(path=self.filepath_image, scale=0.5)

    def _render_smcat_dot(self):
        self._execute_process(
            commands=["smcat", "-T", "pdf", "-I", "scxml", self._filepath_code, "-o", f"{self.filepath_image}.pdf"]
        )  # -d left-right
        self._pdf_save(self.filepath_image)
