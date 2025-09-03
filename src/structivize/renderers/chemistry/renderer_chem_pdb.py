from rdkit import Chem
from rdkit.Chem import Draw

from ...renderer import Renderer


@Renderer.register("chem_pdb")
class RendererChemPdb(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "rdkit": {"size": (500, 500)},
        "obabel": {},
    }

    def _render_rdkit(self):
        mol = Chem.MolFromPDBFile(self._filepath_code)
        Draw.MolToFile(mol, f"{self.filepath_image}.svg", size=self.tool_config["size"])
        self._svg_save(path=self.filepath_image)

    def _render_obabel(self):
        self._execute_process(commands=["obabel", "-ipdb", self._filepath_code, "-O", f"{self.filepath_image}.svg", "-xb", "none", "-xd"])
        self._svg_save(path=self.filepath_image, cropping=False)
