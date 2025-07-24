from rdkit import Chem
from rdkit.Chem import Draw

from ...renderer import Renderer


@Renderer.register("chem_mol")
class RendererChemMol(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "obabel": {},
        "rdkit": {"size": (500, 500)},
    }

    def preprocess_code(self):
        pass

    def _render_obabel(self):
        self._execute_process(["obabel", "-imol", f"{self._filepath_code}", "-O", f"{self.filepath_image}.svg", "-xb", "none", "-xd"])
        self._svg_save(self.filepath_image)

    def _render_rdkit(self):
        mol = Chem.MolFromMolFile(self._filepath_code)
        Draw.MolToFile(mol, f"{self.filepath_image}.svg", size=self.tool_config["size"])
        self._svg_save(self.filepath_image)
