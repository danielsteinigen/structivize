import plotly.io as pio

from ...renderer import Renderer


@Renderer.register("charts_plotly")
class RendererChartsPlotly(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "plotly": {},
    }
    FILE_EXT = "json"

    def preprocess_code(self) -> str:
        self._clean_code_lines("{")
        self._code = self._code.replace(": False", ": false").replace(": True", ": true")
        # TODO: add "margin": {"l": 10, "r": 10, "t": 40, "b": 10}

    def _render_plotly(self):
        fig = pio.from_json(self._code)
        fig.write_image(f"{self.filepath_image}.svg")
        self._svg_save(self.filepath_image)
