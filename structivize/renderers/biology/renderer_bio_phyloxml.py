
import matplotlib.pyplot as plt
from Bio import Phylo
from ete3 import Tree, Phyloxml

from ...renderer import Renderer


@Renderer.register("bio_phyloxml")
class RendererBioPhyloxml(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "biopython": {},
        "ete3": {},
    }

    def verify_code(self):
        return "phyloxml.org" in self._code and "phylogeny" in self._code and self._code.find("phyloxml") < self._code.find("phylogeny")
    
    def _render_biopython(self):
        tree = Phylo.read(self._filepath_code, "phyloxml")
        Phylo.draw(tree) # TODO: also draw_graphviz, to_networkx
        plt.savefig(f"{self.filepath_image}.png")
        plt.close()

    def _render_ete3(self):
        pxm = Phyloxml() # TODO: not working
        pxm.build_from_file(self._filepath_code)
        tree = pxm.get_phylogeny()[0] # Get the first phylogenetic tree in the file
        # tree = Tree(self._filepath_code, format=1)
        tree.render(f"{self.filepath_image}.png", w=800, dpi=300)