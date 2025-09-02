import xml.etree.ElementTree as ET
from collections import Counter

import bpmn_python.bpmn_diagram_rep as diagram
import bpmn_python.bpmn_diagram_visualizer as visualizer
import pm4py
from graphviz import Source

from ...renderer import Renderer, StatisticResponse


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

    def statistics(self) -> StatisticResponse:
        ns = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        tree = ET.ElementTree(ET.fromstring(self._code))
        root = tree.getroot()
        stats = Counter()
        for process in root.findall("bpmn:process", ns):
            stats["start_events"] += len(process.findall("bpmn:startEvent", ns))
            stats["end_events"] += len(process.findall("bpmn:endEvent", ns))
            stats["tasks"] += len(process.findall("bpmn:task", ns))
            stats["exclusive_gateways"] += len(process.findall("bpmn:exclusiveGateway", ns))
            stats["parallel_gateways"] += len(process.findall("bpmn:parallelGateway", ns))

            sequence_flows = process.findall("bpmn:sequenceFlow", ns)
            stats["sequence_flows"] = len(sequence_flows)
            stats["conditional_flows"] = sum(1 for flow in sequence_flows if flow.find("bpmn:conditionExpression", ns) is not None)
        return StatisticResponse(node_types=dict(stats))
