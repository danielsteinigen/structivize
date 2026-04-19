import matplotlib.pyplot as plt
from Bio import Phylo
from ete3 import NodeStyle, TextFace, Tree, TreeStyle

from ...renderer import NodeType, Renderer, StatisticResponse


# Phylogenetic Tree
@Renderer.register("bio_newick")
class RendererBioNewick(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "biopython": {
            "axis": "on",
            "show_confidence": True,
            "thick": 1,
            "style": "seaborn-v0_8-white",
            "term": "#000000",
            "int": "#000000",
            "label": "#000000",
        },
        "ete3": {
            "layout": "c",
            "show_scale": True,
            "line_color": "#000000",
            "line_width": 2,
            "dot_color": "#1ABC9C",
            "dot_size": 6,
            "label_color": "#000000",
        },
    }

    def preprocess_code(self):
        self._clean_code_lines("(")
        self._code = self._code.strip()

    def verify_code(self):
        return self._code and self._code[0] == "(" and (self._is_single_line() or self._code.split("\n")[-1].strip()[0] == ")")

    def _render_biopython(self):
        with plt.style.context(self.tool_config["style"]):
            tree = Phylo.read(self._filepath_code, "newick")

            for clade in tree.find_clades():
                if clade.is_terminal():
                    clade.color = self.tool_config["term"]
                    clade.width = self.tool_config["thick"]
                else:
                    clade.color = self.tool_config["int"]
                    clade.width = self.tool_config["thick"]

            label_color_map = {
                c.name: self.tool_config["label"] if c.is_terminal() else self.tool_config["label"] for c in tree.find_clades() if c.name
            }

            Phylo.draw(tree, do_show=False, show_confidence=self.tool_config["show_confidence"], label_colors=label_color_map)

            if self.tool_config["axis"] == "off":
                plt.axis("off")

            plt.savefig(f"{self.filepath_image}.png")
            plt.close()
            self._png_save(self.filepath_image)

    def _render_ete3(self):
        tree = Tree(self._filepath_code, format=1)

        ts = TreeStyle()
        ts.mode = self.tool_config["layout"]  # "c" or "r"
        ts.show_leaf_name = False
        ts.show_scale = self.tool_config["show_scale"]
        if self.tool_config["layout"] == "c":
            ts.arc_start = -180
            ts.arc_span = 360

        for n in tree.traverse():
            ns = NodeStyle()

            ns["vt_line_color"] = self.tool_config["line_color"]
            ns["hz_line_color"] = self.tool_config["line_color"]
            ns["vt_line_width"] = self.tool_config["line_width"]
            ns["hz_line_width"] = self.tool_config["line_width"]

            ns["shape"] = "circle"
            ns["fgcolor"] = self.tool_config["dot_color"]
            ns["size"] = self.tool_config["dot_size"]

            n.set_style(ns)

            if n.is_leaf():
                tf = TextFace(n.name, fsize=10, fgcolor=self.tool_config["label_color"])
                tf.margin_left = 5
                n.add_face(tf, column=0, position="branch-right")

        tree.render(f"{self.filepath_image}.png", w=800, tree_style=ts, dpi=300)
        self._png_save(self.filepath_image)

    def statistics(self) -> StatisticResponse:
        return StatisticResponse(node_types=[NodeType(type="leaf nodes", count=len(self._code.split(",")))])
