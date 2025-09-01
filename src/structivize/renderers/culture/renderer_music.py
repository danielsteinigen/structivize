import re

from ...renderer import Renderer


class RendererMusic(Renderer):

    def _replace_tagline(self, path):
        with open(path, "r") as file:
            content = file.read()
        content = re.sub(r'tagline\s*=\s*".*?"', 'tagline = ""', content)
        with open(path, "w") as file:
            file.write(content)

    def _conv_abc2ly(self, filepath_code, filepath_img):
        self._execute_process(commands=["abc2ly", "-o", f"{filepath_img}.ly", filepath_code])

    def _conv_xml2ly(self, filepath_code, filepath_img):
        self._execute_process(commands=["musicxml2ly", "-o", f"{filepath_img}", filepath_code])

    def _conv_ly2svg(self, filepath_code, filepath_img):
        self._execute_process(commands=["lilypond", "-dno-point-and-click", "-dresolution=300", "-f", "svg", "-o", filepath_img, filepath_code])
        self._svg_save(filepath_img)
        # other implementation for cropping: add '#(ly:set-option 'crop #t)' to .ly
