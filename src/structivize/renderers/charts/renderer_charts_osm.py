import matplotlib.pyplot as plt
import osmnx as ox

from ...renderer import Renderer


@Renderer.register("charts_osm")
class RendererChartsOsm(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "osmnx": {},
    }
    FILE_EXT = "xml"

    def preprocess_code(self) -> str:
        self._clean_code_lines("<")

    def _render_osmnx(self):
        gdf = ox.features_from_xml(self._filepath_code)
        ax = gdf.plot()
        ax.set_axis_off()
        plt.savefig(f"{self.filepath_image}.png", dpi=300, bbox_inches="tight")
        plt.close()
        self._png_save(self.filepath_image)
