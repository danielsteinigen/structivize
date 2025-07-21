import SBMLDiagrams
import sbmlnetwork

from ...renderer import Renderer


@Renderer.register("bio_sbml")
class RendererBioSbml(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "sbmldiagrams": {},
        "sbmlnetwork": {},
    }

    def preprocess_code(self):
        self.clean_code_lines("<")
        self._code = self._code.strip()
        if not self._code.startswith("<?xml"):
            self._code = f'<?xml version="1.0" encoding="UTF-8"?>\n{self._code}'

        new_lines = []
        for line in self._code.splitlines():
            if line.strip().startswith("<sbml xmlns="):
                new_lines.append('<sbml xmlns="http://www.sbml.org/sbml/level2" level="2" version="1">')
            else:
                new_lines.append(line)
        self._code = "\n".join(new_lines)

    def _render_sbmldiagrams(self):
        df = SBMLDiagrams.load(self._filepath_code)
        # df.setReactionLineThickness("reaction_id", 3.)
        # df.autolayout()
        # df.setColorStyle(colors["simplicity"])
        df.draw(output_fileName=f"{self.filepath_image}.png", scale=2)  # , setImageSize=[600,300]

    def _render_sbmlnetwork(self):
        network = sbmlnetwork.load(self._filepath_code)
        # network.autolayout() # TODO: check why attribute errors appear - maybe update to newer version
        # network.setStyle("escher")
        # network.setSpeciesFillColor('Orange')
        network.draw(f"{self.filepath_image}.pdf")
