import matplotlib.pyplot as plt
from Bio import Phylo
from ete3 import Nexml, Tree

from ...renderer import Renderer


@Renderer.register("bio_nexml")
class RendererBioNexml(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "biopython": {},
        "ete3": {},
    }
    FILE_EXT = "xml"

    def _render_biopython(self):
        tree = Phylo.read(self._filepath_code, "nexml")
        Phylo.draw(tree)
        plt.savefig(f"{self.filepath_image}.png")
        plt.close()

    def _render_ete3(self):
        nexml_project = Nexml()
        nexml_project.build_from_file(self._filepath_code)
        tree_collections = nexml_project.get_trees()
        collection_1 = tree_collections[0]
        tree = collection_1.get_tree()[0]
        # tree = Tree(self._filepath_code, format=1)
        tree.render(f"{self.filepath_image}.png", w=800, dpi=300)
