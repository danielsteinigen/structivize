import os

from ...renderer import Renderer
from ...utils import remove_files
from .renderer_music import RendererMusic


@Renderer.register("music_abc")
class RendererMusicAbc(RendererMusic):
    DEFAULT_TOOL_CONFIGS = {
        "lilypond": {},
        "abcm2ps": {},
    }

    def preprocess_code(self):
        self._clean_code_lines(":")
        code = ""
        for line in self._code.split("\n"):
            line_str = line.strip()
            if not line_str.startswith("T:") and not line_str.startswith("C:") and not line_str.startswith("W:"):
                code += f"{line}\n"
        self._code = code.strip()

    def verify_code(self):
        return self._code.startswith("X:") or self._code.startswith("X :")

    def _render_lilypond(self):
        self._conv_abc2ly(self._filepath_code, self.filepath_image)
        self._replace_tagline(f"{self.filepath_image}.ly")
        self._conv_ly2pdf(f"{self.filepath_image}.ly", self.filepath_image)
        remove_files(self.filepath_image, ["ly", "midi"])

    def _render_abcm2ps(self):
        self._execute_process(
            commands=[f"{self._tool_path}/abcm2ps/abcm2ps", "-g", self._filepath_code, "-O", f"{self.filepath_image}.svg"]
        )
        os.rename(f"{self.filepath_image}001.svg", f"{self.filepath_image}.svg")
        self._svg_save(self.filepath_image)
