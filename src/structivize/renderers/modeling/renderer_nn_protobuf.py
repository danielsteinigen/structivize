from ...renderer import Renderer


@Renderer.register("nn_protobuf")
class RendererNnProtobuf(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "netron": {},
    }

    def preprocess_code(self):
        self._clean_code_lines("{")
        self._code = self._code.strip()

    def _render_netron(self):
        self._execute_process(commands=["netron_export", "--output", f"{self.filepath_image}.svg", self._filepath_code])
        self._svg_save(self.filepath_image)
