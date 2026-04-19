import json

import plotly.io as pio

from ...renderer import NodeType, Renderer, StatisticResponse


@Renderer.register("charts_plotly")
class RendererChartsPlotly(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "plotly": {},
    }
    FILE_EXT = "json"

    def preprocess_code(self) -> str:
        self._clean_code_lines("{")
        self._code = self._code.replace(": False", ": false").replace(": True", ": true")
        code = json.loads(self._code)
        data = code.get("data", [])
        if data and data[0].get("type", "").lower() == "table":
            cells = data[0].get("cells", {})
            values = cells.get("values", [])
            if values and len(values[0]) > 10:
                code.setdefault("layout", {})["margin"] = {"l": 10, "r": 10, "t": 40, "b": 10}
                self._code = json.dumps(code, indent=4, ensure_ascii=False)

    def _render_plotly(self):
        fig = pio.from_json(self._code)
        fig.write_image(f"{self.filepath_image}.svg")
        self._svg_save(self.filepath_image)

    def statistics(self) -> StatisticResponse:
        node_types = {}
        code = json.loads(self._code)
        data = code.get("data", [])
        if data and data[0].get("type", "").lower() == "table":
            cells = data[0].get("cells", {})
            values = cells.get("values", [])
            if values:
                node_types["columns"] = len(values)
                node_types["rows"] = len(values[0])
        elif data and len(data) == 1 and data[0].get("type", "").lower() == "bar":
            node_types["bars"] = len(data[0].get("x", []))
        elif data and len(data) == 1 and data[0].get("type", "").lower() == "pie":
            node_types["slices"] = len(data[0].get("values", []))
        elif data and data[0].get("type", "").lower() == "scatterpolar":
            node_types["series"] = len(data)
        elif data and data[0].get("type", "").lower() == "scatter":
            if all("lines" in item.get("mode", "") for item in data):
                node_types["series"] = len(data)
        elif data and len(data) == 1 and data[0].get("type", "").lower() == "treemap":
            node_types["fields"] = len(data[0].get("labels", []))  # nodes (root, leaf)

        return StatisticResponse(node_types=[NodeType(type=name, count=count) for name, count in node_types.items()])
