import os
import re
from collections import defaultdict

from ...renderer import Renderer, StatisticResponse
from ...utils import remove_files
from .renderer_music import RendererMusic


@Renderer.register("music_abc")
class RendererMusicAbc(RendererMusic):
    DEFAULT_TOOL_CONFIGS = {
        "lilypond": {
            "note_color": "#000000",
            "staff_color": "#000000",
            "time_color": "#000000",
            "note_shape": "default",
            "thickness": 1.0,
            "staff_size": 20,
        },
        # "abcm2ps": {},
    }
    FILE_EXT = "abc"

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
        self._apply_styling(self.filepath_image, self.tool_config)
        self._conv_ly2svg(f"{self.filepath_image}.ly", self.filepath_image)
        remove_files(self.filepath_image, ["ly", "midi"])

    def _render_abcm2ps(self):
        self._execute_process(
            commands=[f"{self._tool_path}/abcm2ps/abcm2ps", "-g", self._filepath_code, "-O", f"{self.filepath_image}.svg"]
        )
        os.rename(f"{self.filepath_image}001.svg", f"{self.filepath_image}.svg")
        self._svg_save(self.filepath_image)

    def statistics(self) -> StatisticResponse:
        counts = defaultdict(int)
        code = re.sub(r"\[.*?\]", "", self._code)  # remove anything in square brackets
        code = re.sub(r'".*?"', "", code)  # remove anything in double quotes
        lines = code.strip().splitlines()
        for line in lines:
            if re.match(r"^[A-Za-z]:", line):  # metadata line like T:, X:, M:, etc.
                continue
            if line.strip().startswith("%"):
                continue
            notes = re.findall(r"[A-Ga-g]", line)
            for note in notes:
                counts[note.upper()] += 1
        return StatisticResponse(node_types=dict(counts))
