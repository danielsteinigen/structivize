from lxml import etree
from rdkit import Chem
from rdkit.Chem import AllChem, Draw

from ...renderer import Renderer
from ...utils import remove_files


@Renderer.register("chem_smarts")
class RendererChemSmarts(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "rdkit": {"size": (500, 500)},
    }

    def verify_code(self):
        return self._is_single_line()

    def _svg_contains_path(self, svg_path, target_class, target_d):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(svg_path, parser)
        root = tree.getroot()

        # Look for all <path> elements
        for path in root.iter("{http://www.w3.org/2000/svg}path"):
            if path.get("class") == target_class and path.get("d") == target_d:
                return True
        return False

    def _render_rdkit(self):
        mol = Chem.MolFromSmarts(self._code)
        Draw.MolToFile(mol, f"{self.filepath_image}.svg", size=self.tool_config["size"])
        self._svg_save(path=self.filepath_image)

        target_d = """m 253.6,266.3 q 0,-3.3 0.7,-5.3 0.7,-2.1 1.7,-3.2 1,-1 2.5,-2.1 1,-0.8 1.6,-1.3 0.6,-0.6 1,-1.4 0.4,-0.8 0.4,-2.1 0,-1.6 -1.2,-2.7 -1.2,-1.2 -3.3,-1.2 -2.6,0 -5.8,1.1 l -0.5,-3.5 q 3,-1 6.2,-1 2.7,0 4.6,1 2,1 2.9,2.7 0.9,1.7 0.9,3.6 0,1.9 -0.5,3.2 -0.5,1.2 -1.2,2 -0.7,0.7 -2,1.6 -1.4,1.1 -2.3,2 -0.8,0.9 -1.4,2.5 -0.6,1.6 -0.6,4.1 h -3.7 m 0,2.6 h 3.7 v 3.5 h -3.7 v -3.5"""
        result = self._svg_contains_path(f"{self.filepath_image}.svg", "atom-0", target_d)

        if result:
            print("Remove Smarts image")
            remove_files(self.filepath_image, ["png", "pdf", "svg"])


@Renderer.register("chem_smarts_reaction")
class RendererChemSmartsReaction(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "rdkit": {},
    }

    def verify_code(self):
        return self._is_single_line()

    # https://www.rdkit.org/docs/GettingStartedInPython.html#drawing-chemical-reactions
    def _render_rdkit(self):
        rxn = AllChem.ReactionFromSmarts(self._code, useSmiles=True)
        d2d = Draw.MolDraw2DCairo(800, 300)
        d2d.DrawReaction(rxn)
        png = d2d.GetDrawingText()
        open(f"{self.filepath_image}.png", "wb+").write(png)
        self._png_save(self.filepath_image)
