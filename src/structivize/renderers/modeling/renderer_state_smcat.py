from ...renderer import Renderer


@Renderer.register("state_smcat")
class RendererStateSmcat(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "smcat": {},
        "smcat_dot": {},
    }

    def _render_smcat_dot(self):
        self._execute_process(
            commands=["smcat", "-T", "pdf", "-I", "smcat", self._filepath_code, "-o", f"{self.filepath_image}.pdf"]
        )  # -d left-right
        self._pdf_save(self.filepath_image)

    def _render_smcat(self):
        self._execute_process(
            commands=["smcat", "-T", "pdf", "-I", "smcat", "-E", "circo", self._filepath_code, "-o", f"{self.filepath_image}.pdf"]
        )
        self._pdf_save(self.filepath_image)
