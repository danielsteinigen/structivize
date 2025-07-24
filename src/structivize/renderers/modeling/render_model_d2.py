from ...renderer import Renderer


@Renderer.register("model_d2")
class RendererModelD2(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "d2": {},
    }

    def _render_d2(self):
        self._execute_process(
            commands=["d2", self._filepath_code, f"{self.filepath_image}.svg"]
        )  # .pdf  --theme 0  https://d2lang.com/tour/themes
        self._svg_save(path=self.filepath_image)
