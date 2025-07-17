
import scadnano as sc

from ...renderer import Renderer


@Renderer.register("bio_scadnano")
class RendererBioScadnano(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "scadnano": {},
    }

    # https://github.com/UC-Davis-molecular-computing/scadnano/blob/main/tutorial/tutorial.md
    def _render_scadnano(self):
        design = sc.Design.from_scadnano_file(self._filepath_code) # from_cadnano_v2()
        # design = sc.Design(helical_pitch=10.5)
        # design.add_strand(sc.Strand([sc.Domain(helix=0, start=0, end=16)]))
        # design.add_strand(sc.Strand([sc.Domain(helix=1, start=0, end=16)]))
        design.write_png_file(f"{self.filepath_image}.png") # not possible