from sismic.io import export_to_plantuml, import_from_yaml
from sismic.model import Statechart

from ...renderer import Renderer
from .renderer_model_plantuml import RendererModelPlantuml


@Renderer.register("state_sismic")
class RendererStateSismic(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "sismic": {},
    }

    def _render_sismic(self):
        statechart = import_from_yaml(filepath=self._filepath_code)
        assert isinstance(statechart, Statechart)
        export_to_plantuml(
            statechart=statechart,
            filepath=f"{self.filepath_image}.plantuml",
            state_action=True,
            state_contracts=True,
            transition_contracts=True,
            transition_action=True,
        )
        renderer = RendererModelPlantuml(output_base_path=self.filepath_image, code_path=f"{self.filepath_image}.plantuml")
        result = renderer.render()
