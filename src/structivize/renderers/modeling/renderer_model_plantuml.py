import os

from ...renderer import Renderer


@Renderer.register("model_plantuml")
class RendererModelPlantuml(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "plantuml": {},
    }

    def preprocess_code(self):
        self.clean_code_lines("@")
        for x in ["@startuml", "@startmindmap", "@startchen", "@startgantt"]:
            self._code = self._code.strip().replace(x, f"{x} {self._filepath_image.split('/')[-1]}\nskinparam dpi 300")

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
