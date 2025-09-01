import pydot
from graphviz import Source

from ...renderer import Renderer
from ...utils import remove_files


@Renderer.register("model_dot")
class RendererModelDot(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "graphviz": {},
        "pydot": {},
    }

    def preprocess_code(self):
        self._clean_code_lines("{")
        self._code = self._code.strip()

    def _render_graphviz(self):
        src = Source(self._code)
        src.render(self.filepath_image, format="png", view=False)
        remove_files(self.filepath_image)

    def _render_pydot(self):
        graphs = pydot.graph_from_dot_data(self._code)
        graph = graphs[0]
        graph.write_png(f"{self.filepath_image}.png")
