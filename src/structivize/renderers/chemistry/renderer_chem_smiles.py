from rdkit import Chem
from rdkit.Chem import Draw
from collections import Counter

from ...renderer import Renderer


@Renderer.register("chem_smiles")
class RendererChemSmiles(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "rdkit": {"size": (500, 500)},
        "obabel": {},
    }

    def verify_code(self):
        return self._is_single_line()

    def _render_rdkit(self):
        mol = Chem.MolFromSmiles(self._code)
        Draw.MolToFile(mol, f"{self.filepath_image}.svg", size=self.tool_config["size"])
        self._svg_save(path=self.filepath_image)
        # d = Draw.rdMolDraw2D.MolDraw2DCairo(500, 500)
        # Draw.rdMolDraw2D.PrepareAndDrawMolecule(d,mol)
        # d.WriteDrawingText(f"{self.filepath_image}.png")

    def _render_obabel(self):
        self._execute_process(
            commands=["obabel", "-ismiles", self._filepath_code, "-O", f"{self.filepath_image}.svg", "-xb", "none", "-xd"]
        )  # -xa draw all carbon atoms
        self._svg_save(path=self.filepath_image, cropping=False)

    def statistics(self) -> StatisticResponse:
        mol = Chem.MolFromSmiles(self._code)
        # num_atoms = mol.GetNumAtoms() # Number of atoms 19
        # num_bonds = mol.GetNumBonds() # Number of bonds 21
        # num_heavy_atoms = mol.GetNumHeavyAtoms() # Number of heavy atoms (non-hydrogens) 19
        # mol_weight = Descriptors.MolWt(mol) # Molecular weight
        # formula = rdMolDescriptors.CalcMolFormula(mol) # Formula

        # Atom counts by element
        atom_symbols = [atom.GetSymbol() for atom in mol.GetAtoms()]
        atom_counts = Counter(atom_symbols)
        renamed_counts = {f"{el} atoms": count for el, count in atom_counts.items()}
        renamed_counts["rings"] = rdMolDescriptors.CalcNumRings(mol) # Number of rings 3

        return StatisticResponse(node_types=dict(renamed_counts))