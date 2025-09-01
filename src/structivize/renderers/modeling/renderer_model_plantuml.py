import os
import re
from collections import defaultdict

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
        def parse_class(code):
            counts = defaultdict(int)
            lines = self._code.strip().splitlines()
            in_class_block = False

            for line in lines:
                line = line.strip()
                if re.match(r'^(abstract\s+)?class\s+', line) or line.startswith('interface'):
                    counts['classes'] += 1
                    in_class_block = True
                elif in_class_block and line.startswith('}'):
                    in_class_block = False
                # elif in_class_block and re.match(r'^[+#-]?[A-Za-z_]+\s+[A-Za-z_<>]+', line):
                #     counts['attributes'] += 1
            return StatisticResponse(node_types=dict(counts))

        def parse_component(code):
            counts = defaultdict(int)
            lines = self._code.strip().splitlines()
            for line in lines:
                line = line.strip()
                if '[' in line and ']' in line and '>' not in line:
                    matches = re.findall(r'\[.*?\]', line)
                    counts['components'] += len(matches)
            return StatisticResponse(node_types=dict(counts))


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
