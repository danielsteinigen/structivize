import asyncio
import re

from ...renderer import Renderer
from ..browser_control import export_markmap


@Renderer.register("model_markmap")
class RendererModelMarkmap(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "markmap": {},
    }

    def __replace_tags(self, text):
        def replacer(match):
            tag = match.group(1)
            attrs = match.group(2)

            alt_match = re.search(r'alt="([^"]*)"', attrs)
            src_match = re.search(r'src="([^"]*)"', attrs)

            if alt_match:
                return alt_match.group(1)
            elif src_match:
                return src_match.group(1)
            else:
                return tag

        pattern = r"<([a-zA-Z0-9]+)\b([^>]*)>"
        return re.sub(pattern, replacer, text)

    def preprocess_code(self):
        self._clean_code_lines("#")
        self._code = self.__replace_tags(self._code).strip().replace("- #", "#")

    def _render_markmap(self):
        self._execute_process(
            commands=[
                "npx",
                "markmap-cli",
                "--no-open",
                "--no-toolbar",
                "-o",
                f"{self.filepath_image}.html",
                "--offline",
                self._filepath_code,
            ]
        )
        asyncio.run(export_markmap(self.filepath_image, self._max_width, self._max_height))
        self._svg_save(path=f"{self.filepath_image}_2")
