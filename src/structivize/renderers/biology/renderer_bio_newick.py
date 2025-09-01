import matplotlib.pyplot as plt
from Bio import Phylo
from ete3 import Tree

from ...renderer import Renderer, StatisticResponse


# Phylogenetic Tree
@Renderer.register("bio_newick")
class RendererBioNewick(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "biopython": {},
        "ete3": {},
    }

    def preprocess_code(self):
        self._clean_code_lines("(")
        self._code = self._code.strip()

    def verify_code(self):
        return self._code[0] == "(" and (self._is_single_line() or self._code.split("\n")[-1].strip()[0] == ")")

    def _render_biopython(self):
        tree = Phylo.read(self._filepath_code, "newick")
        Phylo.draw(tree)
        plt.savefig(f"{self.filepath_image}.png")
        plt.close()

    def _render_ete3(self):
        tree = Tree(self._filepath_code, format=1)
        tree.render(f"{self.filepath_image}.png", w=800, dpi=300)


    def statistics(self) -> StatisticResponse:
        return StatisticResponse(node_types={"leaf nodes": len(self._code.split(","))})