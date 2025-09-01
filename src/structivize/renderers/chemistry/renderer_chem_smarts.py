from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, Draw

from ...image_utils import images_are_similar
from ...renderer import Renderer
from ...utils import remove_files


@Renderer.register("chem_smarts")
class RendererChemSmarts(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "rdkit": {"size": (500, 500)},
    }

    def verify_code(self):
        return self._is_single_line()

    def _render_rdkit(self):
        mol = Chem.MolFromSmarts(self._code)
        Draw.MolToFile(mol, f"{self.filepath_image}.svg", size=self.tool_config["size"])
        self._svg_save(path=self.filepath_image)

        reference_path = Path(__file__).parent.parent.parent.parent.parent / "examples/reference/false_ref_smarts.png"
        result = images_are_similar(f"{self.filepath_image}.png", f"{reference_path}", tolerance=5)
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
