from ...renderer import Renderer


@Renderer.register("draw_ditaa")
class RendererDrawDitaa(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "ditaa": {},
    }

    def _render_ditaa(self):
        self._execute_process(
            commands=["java", "-jar", f"{self._tool_path}/ditaa0_9.jar", self._filepath_code, f"{self.filepath_image}.png"]
        )
