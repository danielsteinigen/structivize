import matplotlib.pyplot as plt
import networkx as nx
from graphviz import Source

from ...renderer import Renderer
from ...utils import load_text, remove_files


# Graph Modelling Language
@Renderer.register("graph_gml")
class RendererGraphGml(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "networkx": {},
        "graphviz": {},
    }
    FILE_EXT = "gml"

    def preprocess_code(self):
        self._clean_code_lines("graph")
        self._code = self._code.strip()

    def _render_networkx(self):
        G = nx.Graph()
        G = nx.read_gml(self._filepath_code, label="id")
        plt.figure(figsize=(10, 6))
        nx.draw(G, with_labels=True)
        plt.savefig(f"{self.filepath_image}.png", dpi=300, bbox_inches="tight")
        plt.close()
        self._png_save(self.filepath_image)

    def _render_graphviz(self):
        self._execute_process(commands=["gml2gv", "-o", f"{self.filepath_image}.dot", self._filepath_code])
        src = Source(load_text(f"{self.filepath_image}.dot"))
        src.render(self.filepath_image, format="png", view=False)
        self._png_save(self.filepath_image)
        remove_files(self.filepath_image, ["", "dot"])
