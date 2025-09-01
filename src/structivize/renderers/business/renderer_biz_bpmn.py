import bpmn_python.bpmn_diagram_rep as diagram
import bpmn_python.bpmn_diagram_visualizer as visualizer
import pm4py
from graphviz import Source

from ...renderer import Renderer


@Renderer.register("biz_bpmn")
class RendererBizBpmn(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "bpmnpython": {},
        "pm4py": {},
    }
    FILE_EXT = "xml"

    def preprocess_code(self):
        self._clean_code_lines("<")
        self._code = self._code.strip()
        if not self._code.startswith("<?xml"):
            self._code = f'<?xml version="1.0" encoding="UTF-8"?>\n{self._code}'

    def _render_bpmnpython(self):
        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(self._filepath_code)

        visualizer.bpmn_diagram_to_png(bpmn_graph, self.filepath_image)
        visualizer.bpmn_diagram_to_dot_file(bpmn_graph, self.filepath_image)
        # src = Source.from_file(f"{self.filepath_image}.dot") # .dot file seems to be not saved correctly
        # src.render(self.filepath_image, format="pdf", view=False)

    def _render_pm4py(self):
        bpmn = pm4py.read_bpmn(self._filepath_code)
        pm4py.save_vis_bpmn(bpmn_graph=bpmn, file_path=f"{self.filepath_image}.pdf", rankdir="TB")
        self._pdf_save(self.filepath_image)
