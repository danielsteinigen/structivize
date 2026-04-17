from collections import Counter

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, Draw, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D

from ...renderer import Renderer, StatisticResponse


@Renderer.register("chem_smiles")
class RendererChemSmiles(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "rdkit": {"width": 500, "height": 500, "bond_width": 2, "font_size": 18, "background_color": "#FFFFFF", "carbon_color": "#000000"},
        "obabel": {"background_color": "none", "bond_color": "#555555"},
    }

    def verify_code(self):
        return self._is_single_line()

    # def _render_rdkit(self):
    #     mol = Chem.MolFromSmiles(self._code)
    #     Draw.MolToFile(mol, f"{self.filepath_image}.svg", size=(500, 500))
    #     self._svg_save(path=self.filepath_image)
    #     # d = Draw.rdMolDraw2D.MolDraw2DCairo(500, 500)
    #     # Draw.rdMolDraw2D.PrepareAndDrawMolecule(d,mol)
    #     # d.WriteDrawingText(f"{self.filepath_image}.png")

    def _render_rdkit(self):
        mol = Chem.MolFromSmiles(self._code)
        if self.tool_config.get("explicit_hydrogens", False):
            mol = Chem.AddHs(mol)

        AllChem.Compute2DCoords(mol)
        width = self.tool_config.get("width", 500)
        height = self.tool_config.get("height", 500)
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)

        opts = drawer.drawOptions()
        opts.addStereoAnnotation = self.tool_config.get("show_stereo", False)  # Adds (R)/(S)
        opts.explicitMethyl = self.tool_config.get("explicit_methyl", False)  # Adds -CH3 labels
        opts.addAtomIndices = self.tool_config.get("show_indices", False)
        opts.bondLineWidth = self.tool_config.get("bond_width", 2)
        opts.minFontSize = self.tool_config.get("min_font_size", 12)
        opts.comicMode = self.tool_config.get("comic_mode", False)

        def hex_to_rgb(hex_str):
            hex_str = hex_str.lstrip("#")
            return tuple(int(hex_str[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

        bg_hex = self.tool_config.get("background_color", "#FFFFFF")
        if bg_hex != "transparent":
            opts.setBackgroundColour(hex_to_rgb(bg_hex))
        else:
            opts.clearBackground = False

        if "carbon_color" in self.tool_config:
            c_rgb = hex_to_rgb(self.tool_config["carbon_color"])
            opts.updateAtomPalette({6: c_rgb})

        if self.tool_config.get("force_light_atoms", False):
            opts.updateAtomPalette(
                {
                    7: (0.6, 0.8, 1.0),  # Light Blue N
                    8: (1.0, 0.6, 0.6),  # Light Red O
                    16: (1.0, 1.0, 0.6),  # Light Yellow S
                    9: (0.6, 1.0, 0.6),  # Light Green F
                    17: (0.6, 1.0, 0.6),  # Light Green Cl
                }
            )

        if self.tool_config.get("bw_palette", False):
            opts.useBWAtomPalette()

        # 3. Draw and Save
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()

        svg_content = drawer.GetDrawingText()
        self._svg_save(path=self.filepath_image, svg_code=svg_content)

    def _render_obabel(self):
        cmd = ["obabel", "-ismiles", self._filepath_code, "-O", f"{self.filepath_image}.svg"]

        cmd.extend(["-xb", self.tool_config.get("background_color", "none")])
        if "bond_color" in self.tool_config:
            cmd.extend(["-xB", self.tool_config["bond_color"]])

        if self.tool_config.get("draw_all_carbons", False):
            cmd.append("-xa")

        if self.tool_config.get("no_terminal_carbons", False):
            cmd.append("-xC")

        if self.tool_config.get("thick_lines", False):
            cmd.append("-xt")

        if not self.tool_config.get("show_name", False):
            cmd.append("-xd")

        if self.tool_config.get("add_hydrogens", False):
            cmd.append("-h")

        self._execute_process(commands=cmd)

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
        renamed_counts["rings"] = rdMolDescriptors.CalcNumRings(mol)  # Number of rings 3

        return StatisticResponse(node_types=dict(renamed_counts))
