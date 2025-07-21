from rdkit import Chem
from rdkit.Chem import Draw

from ...renderer import Renderer


# Chemical Identifier (InChI) for chemical structures
@Renderer.register("chem_inchi")
class RendererChemInchi(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "rdkit": {"size": (500, 500)},
        "obabel": {},
    }

    def verify_code(self):
        return self._is_single_line()

    def _render_rdkit(self):
        mol = Chem.MolFromInchi(self._code)
        Draw.MolToFile(mol, f"{self.filepath_image}.svg", size=self.tool_config["size"])
        self._svg_save(path=self.filepath_image)

    def _render_obabel(self):
        self._execute_process(commands=["obabel", "-iinchi", self._filepath_code, "-O", f"{self.filepath_image}.svg", "-xb", "none", "-xd"])
        self._svg_save(path=self.filepath_image)
