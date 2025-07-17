
from ...renderer import Renderer

@Renderer.register("bio_ct")
class RendererBioCt(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "varna": {},
    }

    def _render_varna(self):
        self._execute_process(commands=["java", "-cp", f"{self._tool_path}/VARNAv3-93.jar", "fr.orsay.lri.varna.applications.VARNAcmd", "-i", self._filepath_code, "-o", f"{self.filepath_image}.png", "-titleSize", "0", "-resolution", "'2.0'", "-zoom", "1.0", "-border", "'20x30'", "-algorithm", "radiate"])
