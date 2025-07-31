from ...renderer import Renderer
from .renderer_music import RendererMusic


@Renderer.register("music_lilypond")
class RendererMusicLy(RendererMusic):
    DEFAULT_TOOL_CONFIGS = {
        "lilypond": {},
    }

    def preprocess_code(self):
        self.clean_code_lines("\\")
        self._code = '\\header {tagline = ""}\n' + self._code
        self._code = self._code.strip()

        code = ""
        for line in self._code.split("\n"):
            line_str = line.strip()
            if (
                not line_str.startswith("title")
                and not line_str.startswith("composer")
                and not line_str.startswith(r"\line")
                and not line_str.startswith(r"\mark")
                and "instrumentName" not in line_str
            ):
                code += f"{line}\n"
        self._code = code.strip()

    def _render_lilypond(self):
        self._conv_ly2pdf(self._filepath_code, self.filepath_image)
