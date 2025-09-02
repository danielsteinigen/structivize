
from collections import defaultdict, Counter
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
        if self._category and self._category == "gantt":
            return StatisticResponse(node_types={"sections": self._code.count("section"), "time bars": self._code.count(":")}) # "tasks": code.count(":")

        elif self._category and self._category == "mind":
            return StatisticResponse(node_types={"nodes": len(self._code.splitlines())-2})

        elif self._category and self._category in ["bpmn", "activity"]:
            counts = defaultdict(int)
            # Count square bracket nodes
            counts['nodes'] = len(re.findall(r'\[[^\[\]]+\]', self._code))
            # Count decision (curly bracket) nodes
            counts['decisions'] = len(re.findall(r'\{[^\{\}]+\}', self._code))
            return StatisticResponse(node_types=dict(counts))

        elif self._category and self._category == "sequence":
            lines = self._code.strip().splitlines()
            stats = Counter()
            message_pattern = re.compile(r'^\w+\s*[-]{1,2}>>?\s*\w+')
            for line in lines:
                line = line.strip()
                if message_pattern.match(line):
                    stats['messages'] += 1
                elif line.startswith('participant ') or line.startswith('actor '):
                    stats['participants'] += 1
                elif line.startswith('activate '):
                    stats['activations'] += 1
                elif line.startswith('deactivate '):
                    stats['deactivations'] += 1
            return StatisticResponse(node_types=dict(stats))
        
        elif self._category and self._category == "state":
            lines = self._code.strip().splitlines()
            stats = Counter()
            states = set()
            transition_pattern = re.compile(r'^\s*(.+?)\s*-->\s*(.+?)(?:\s*:\s*(.+))?$')
            for line in lines:
                match = transition_pattern.match(line)
                if match:
                    src, dst, label = match.groups()
                    stats['transitions'] += 1
                    if src.strip() == '[*]':
                        stats['start_transitions'] += 1
                    else:
                        states.add(src.strip())
                    if dst.strip() == '[*]':
                        stats['end_transitions'] += 1
                    else:
                        states.add(dst.strip())
                    if label:
                        stats['labeled_transitions'] += 1

            stats['states'] = len(states)
            return StatisticResponse(node_types=dict(stats))
        
        else:
            return StatisticResponse()
        
    # def _render_api(self):
    #     graphbytes = self._code.encode("utf8")
    #     base64_bytes = base64.urlsafe_b64encode(graphbytes)
    #     base64_string = base64_bytes.decode("ascii")
    #     img_url = "https://mermaid.ink/img/" + base64_string

    #     img_data = requests.get(img_url).content
    #     with open(f'{self.filepath_image}.png', 'wb') as handler:
    #         handler.write(img_data)
