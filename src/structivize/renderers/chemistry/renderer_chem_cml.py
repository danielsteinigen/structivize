from rdkit import Chem
from rdkit.Chem import Draw

from ...renderer import Renderer
from ...utils import load_text, remove_files


@Renderer.register("chem_cml")
class RendererChemCml(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "obabel": {},
        "rdkit": {"size": (500, 500)},
    }

    def preprocess_code(self):
        self.clean_code_lines("<")
        self._code = self._code.strip()
        if not self._code.startswith("<?xml"):
            self._code = f'<?xml version="1.0" encoding="UTF-8"?>\n{self._code}'

    def _render_obabel(self):
        self._execute_process(commands=["obabel", "-icml", self._filepath_code, "-O", f"{self.filepath_image}.svg", "-xb", "none", "-xd"])
        self._svg_save(path=self.filepath_image)

    def _render_rdkit(self):
        self._execute_process(
            commands=["obabel", "-icml", self._filepath_code, "-O", f"{self.filepath_image}.smiles", "-xb", "none", "-xd"]
        )
        mol = Chem.MolFromSmiles(load_text(f"{self.filepath_image}.smiles"))
        Draw.MolToFile(mol, f"{self.filepath_image}.svg", size=self.tool_config["size"])
        self._svg_save(path=self.filepath_image)
        remove_files(self.filepath_image, ["smiles"])
