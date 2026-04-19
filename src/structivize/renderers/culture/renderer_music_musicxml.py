from ...renderer import Renderer
from ...utils import insert_line, remove_files
from .renderer_music import RendererMusic


@Renderer.register("music_xml")
class RendererMusicXml(RendererMusic):
    DEFAULT_TOOL_CONFIGS = {
        "lilypond": {},
        "musescore": {},
    }
    FILE_EXT = "xml"

    def preprocess_code(self):
        self._clean_code_lines("<")
        self._code = self._code.strip()
        if not self._code.startswith("<?xml"):
            self._code = f'<?xml version="1.0" encoding="UTF-8"?>\n{self._code}'

        # code = ""
        # for line in self._code.split("\n"):
        #     line_str = line.strip()
        #     if (
        #         not line_str.startswith("<part-name")
        #         and not line_str.startswith("<words")
        #         and not line_str.startswith("<creator")
        #         and not line_str.startswith("<work-title")
        #         and not line_str.startswith("<movement-title")
        #         and not line_str.startswith("<rights")
        #     ):
        #         code += f"{line}\n"
        # self._code = code.strip()

    def _render_lilypond(self):
        self._conv_xml2ly(self._filepath_code, self.filepath_image)
        insert_line(f"{self.filepath_image}.ly", '\\header {tagline = ""}\n')
        self._conv_ly2svg(f"{self.filepath_image}.ly", self.filepath_image)
        remove_files(self.filepath_image, ["ly"])

    def _render_musescore(self):
        self._execute_process(commands=["xvfb-run", "musescore3", "-o", f"{self.filepath_image}.pdf", self._filepath_code])
        self._pdf_save(path=self.filepath_image)
