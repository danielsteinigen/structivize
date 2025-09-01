from ...renderer import Renderer


@Renderer.register("nn_onnx")
class RendererNnOnnx(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "netron": {},
    }
    FILE_EXT = "onnx"

    def _render_netron(self):
        self._execute_process(commands=["netron_export", "--output", f"{self.filepath_image}.svg", self._filepath_code])
        self._svg_save(self.filepath_image)
