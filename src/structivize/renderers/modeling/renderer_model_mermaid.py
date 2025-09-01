
from collections import defaultdict
import re
from ...renderer import Renderer, StatisticResponse


@Renderer.register("model_mermaid")
class RendererModelMermaid(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "mermaid": {},
    }
    FILE_EXT = "mmd"

    def _render_mermaid(self):
        self._execute_process(
            commands=["mmdc", "-i", self._filepath_code, "-s", "4", "-o", f"{self.filepath_image}.png"]
        )  # -t dark -b transparent
        # Theme of the chart (choices: "default", "forest", "dark", "neutral", default: "default")

    def statistics(self) -> StatisticResponse:
        def parse_gantt(code):
            return StatisticResponse(node_types={"sections": self._code.count("section"), "time bars": self._code.count(":")}) # "tasks": code.count(":")

        def parse_mind(code):
            return StatisticResponse(node_types={"nodes": len(self._code.splitlines())-2})

        def parse_flowchart(code):
            counts = defaultdict(int)
            # Count square bracket nodes
            counts['nodes'] = len(re.findall(r'\[[^\[\]]+\]', self._code))
            # Count decision (curly bracket) nodes
            counts['decisions'] = len(re.findall(r'\{[^\{\}]+\}', self._code))
            return StatisticResponse(node_types=dict(counts))

    # def _render_api(self):
    #     graphbytes = self._code.encode("utf8")
    #     base64_bytes = base64.urlsafe_b64encode(graphbytes)
    #     base64_string = base64_bytes.decode("ascii")
    #     img_url = "https://mermaid.ink/img/" + base64_string

    #     img_data = requests.get(img_url).content
    #     with open(f'{self.filepath_image}.png', 'wb') as handler:
    #         handler.write(img_data)
