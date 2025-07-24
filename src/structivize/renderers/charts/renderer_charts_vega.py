import json

import altair as alt

from ...renderer import Renderer


@Renderer.register("renderer_charts_vega")
class RendererChartsVega(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "vega": {},
    }

    def preprocess_code(self) -> str:
        self.clean_code_lines("{")
        self._code = self._code.replace(": False", ": false").replace(": True", ": true")

    def _render_vega(self):
        vega_json = json.loads(self._code)
        chart = alt.Chart.from_dict(vega_json)  # supports only VegaLite
        chart.save(f"{self.filepath_image}.svg", scale_factor=2)  # ppi=200
        self._svg_save(self.filepath_image)
