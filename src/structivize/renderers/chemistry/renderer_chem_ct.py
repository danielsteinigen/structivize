from ...renderer import Renderer


@Renderer.register("chem_ct")
class RendererChemCt(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "obabel": {},
    }

    def _render_obabel(self):
        self._execute_process(commands=["obabel", "-ict", self._filepath_code, "-O", f"{self.filepath_image}.svg", "-xb", "none", "-xd"])
        self._svg_save(path=self.filepath_image)
