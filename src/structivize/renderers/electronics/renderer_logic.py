from pathlib import Path

import schemdraw
from schemdraw.parsing import logicparse
from schemdraw.parsing.buchheim import buchheim
from schemdraw.parsing.logic_parser import parse_string, to_tree

from ...image_utils import images_are_similar
from ...renderer import Renderer, StatisticResponse
from ...utils import extract_part, remove_files


@Renderer.register("logic")
class RendererLogic(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "schemdraw": {},
    }

    def preprocess_code(self) -> str:
        self._code = self._code.strip()
        self._code = extract_part(self._code, "=", "", False)
        code = ""
        for line in self._code.split("\n"):
            line_str = line.strip()
            if not line_str.startswith("//") and not line_str.startswith("#"):
                code += f"{line}\n"
        self._code = (
            code.strip()
            .replace("NAND", "nand")
            .replace("XNOR", "xnor")
            .replace("NOR", "nor")
            .replace("XOR", "xor")
            .replace("AND", "and")
            .replace("OR", "or")
            .replace("NOT", "not")
        )

    def verify_code(self):
        return self._is_single_line()

    def _render_schemdraw(self):
        stat = self.statistics().node_types
        if not (stat["and"] == 1 and all(v == 0 for k, v in stat.items() if k != "and")):
            with schemdraw.Drawing(file=f"{self.filepath_image}.svg", show=False):
                logicparse(self._code)
            self._svg_save(self.filepath_image)

    def _countit(self, root, elmdefs, depth=0):
        if root.node not in elmdefs:
            elmdefs["and"] += 1
        else:
            elmdefs[root.node] += 1
        for child in root.children:
            if child.node in elmdefs:
                self._countit(child, elmdefs, depth + 1)  # recursive

    def statistics(self) -> StatisticResponse:
        parsed = parse_string(self._code)
        tree = to_tree(parsed)
        dtree = buchheim(tree)
        elmdefs = {"and": 0, "or": 0, "xor": 0, "nand": 0, "xnor": 0, "nor": 0, "not": 0}
        self._countit(dtree, elmdefs)
        return StatisticResponse(node_types=elmdefs)
