import os
import re
from collections import Counter, defaultdict

from ...renderer import Renderer, StatisticResponse


@Renderer.register("model_plantuml")
class RendererModelPlantuml(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "plantuml": {},
    }
    FILE_EXT = "puml"

    def preprocess_code(self):
        self._clean_code_lines("@")
        for x in ["@startuml", "@startmindmap", "@startchen", "@startgantt"]:
            self._code = self._code.strip().replace(x, f"{x} {str(self._output_base_path).split('/')[-1]}\nskinparam dpi 300")

    def _render_plantuml(self):
        self._execute_process(
            commands=[
                "java",
                "-jar",
                f"{self._tool_path}/plantuml-mit-1.2025.2.jar",
                "-failfast",
                "-o",
                os.path.dirname(os.path.abspath(self.filepath_image)),
                self._filepath_code,
            ]
        )
        # -theme xxx "-xmlstats", "-tsvg",
        # self._svg_save(path=self.filepath_image)

    def statistics(self) -> StatisticResponse:
        if self._category and self._category == "class":
            counts = defaultdict(int)
            lines = self._code.strip().splitlines()
            in_class_block = False

            for line in lines:
                line = line.strip()
                if re.match(r"^(abstract\s+)?class\s+", line) or line.startswith("interface"):
                    counts["classes"] += 1
                    in_class_block = True
                elif in_class_block and line.startswith("}"):
                    in_class_block = False
                # elif in_class_block and re.match(r'^[+#-]?[A-Za-z_]+\s+[A-Za-z_<>]+', line):
                #     counts['attributes'] += 1
            return StatisticResponse(node_types=dict(counts))

        elif self._category and self._category == "component":
            counts = defaultdict(int)
            lines = self._code.strip().splitlines()
            for line in lines:
                line = line.strip()
                if "[" in line and "]" in line and ">" not in line:
                    matches = re.findall(r"\[.*?\]", line)
                    counts["components"] += len(matches)
            return StatisticResponse(node_types=dict(counts))

        elif self._category and self._category == "sequence":
            lines = self._code.strip().splitlines()
            stats = Counter()
            message_pattern = re.compile(r"^\w+\s*[-]{1,2}>>?\s*\w+")
            for line in lines:
                line = line.strip()
                if message_pattern.match(line):
                    stats["messages"] += 1
                elif line.startswith("participant ") or line.startswith("actor "):
                    stats["participants"] += 1
                elif line.startswith("activate "):
                    stats["activations"] += 1
                elif line.startswith("deactivate "):
                    stats["deactivations"] += 1
            return StatisticResponse(node_types=dict(stats))

        elif self._category and self._category == "state":
            lines = self._code.strip().splitlines()
            stats = Counter()
            states = set()
            transition_pattern = re.compile(r"^\s*(.+?)\s*-->\s*(.+?)(?:\s*:\s*(.+))?$")
            for line in lines:
                match = transition_pattern.match(line)
                if match:
                    src, dst, label = match.groups()
                    stats["transitions"] += 1
                    if src.strip() == "[*]":
                        stats["start_transitions"] += 1
                    else:
                        states.add(src.strip())
                    if dst.strip() == "[*]":
                        stats["end_transitions"] += 1
                    else:
                        states.add(dst.strip())
                    if label:
                        stats["labeled_transitions"] += 1

            stats["states"] = len(states)
            return StatisticResponse(node_types=dict(stats))

        elif self._category and self._category == "mind":
            return StatisticResponse(node_types={"nodes": sum(1 for line in self._code.splitlines() if line.strip().startswith("*")) - 1})
        else:
            return StatisticResponse()

    # def _render_api(self):
    #     output = render(
    #         self._code,
    #         engine='plantuml',  # graphviz, ditaa
    #         format="png",       # png, svg
    #         cacheopts={
    #             'use_cache': False
    #         }
    #     )
    #     save_bytes(filename=f"{self.filepath_image}.png", data=output[0])
