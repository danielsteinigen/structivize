from ...renderer import Renderer
from .renderer_db_dbml import RendererDbDbml


@Renderer.register("db_postgresql")
class RendererDbPostgres(RendererDbDbml):
    DEFAULT_TOOL_CONFIGS = {
        "dbml_renderer": {},
    }

    def preprocess_code(self):
        # self._clean_code_lines("(")
        self._code = self._code.strip()

    def _render_dbml_renderer(self):
        self._execute_process(commands=["sql2dbml", "--postgres", self._filepath_code, "-o", f"{self.filepath_image}.dbml"])
        self._render_dbml(f"{self.filepath_image}.dbml", self.filepath_image)
