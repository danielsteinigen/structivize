import geopandas as gpd
import geoplot as gplt
import geoplot.crs as gcrs
import matplotlib.pyplot as plt

from ...renderer import Renderer


@Renderer.register("charts_geojson")
class RendererChartsGeojson(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "geopandas": {},
        "geoplot": {},
    }
    FILE_EXT = "json"

    def preprocess_code(self) -> str:
        self._clean_code_lines("{")
        self._code = self._code.replace(": False", ": false").replace(": True", ": true")

    def _render_geopandas(self):        
        gdf = gpd.read_file(self._filepath_code)
        ax = gdf.plot()
        ax.set_axis_off()
        plt.savefig(f"{self.filepath_image}.png", dpi=300, bbox_inches="tight")
        plt.close()
        self._png_save(self.filepath_image)

    def _render_geoplot(self):        
        gdf = gpd.read_file(self._filepath_code)
        # gplt.polyplot(gdf)
        gplt.polyplot(
            gdf,
            projection=gcrs.AlbersEqualArea(), # TODO: what are projections doing?
            edgecolor='darkgrey',
            facecolor='lightgrey',
            linewidth=.3,
            figsize=(12, 8)
        )
        plt.savefig(f"{self.filepath_image}.png", dpi=300, bbox_inches="tight")
        plt.close()
        self._png_save(self.filepath_image)
