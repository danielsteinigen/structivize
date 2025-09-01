from ...renderer import Renderer


@Renderer.register("db_dbml")
class RendererDbDbml(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "dbml_renderer": {},
    }
    FILE_EXT = "dbml"

    def preprocess_code(self):
        self._clean_code_lines("{")
        self._code = self._code.strip()

    def _render_dbml(self, filepath_code, filepath_image):
        self._execute_process(commands=["dbml-renderer", "-i", filepath_code, "-o", f"{filepath_image}.svg"])
        self._svg_save(path=filepath_image, scale=0.5)

    def _render_dbml_renderer(self):
        self._render_dbml(self._filepath_code, self.filepath_image)
