from ...renderer import Renderer


@Renderer.register("draw_asymptote")
class RendererAsymptote(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "asymptote": {},
    }

    def _render_asymptote(self):
        # https://asymptote.sourceforge.io/doc/index.html

        # os.system(f"xvfb-run asy -f pdf {self._filepath_code} -o {self._filepath_image}")
        self._execute_process(
            commands=["xvfb-run", "asy", "-f", "eps", self._filepath_code, "-o", self.filepath_image, "-render", "16"]
        )  # 16 is the number of dots computed per bp
        self._execute_process(commands=["convert", "-density", "500", f"{self.filepath_image}.eps", f"{self.filepath_image}.pdf"])
        self._pdf_save(path=self.filepath_image)
