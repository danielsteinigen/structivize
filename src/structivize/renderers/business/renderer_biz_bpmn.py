import xml.etree.ElementTree as ET
from collections import Counter

import pm4py
from graphviz import Digraph, Source

from ...renderer import NodeType, Renderer, StatisticResponse


@Renderer.register("biz_bpmn")
class RendererBizBpmn(Renderer):
    DEFAULT_TOOL_CONFIGS = {
        "graphviz": {},
        "pm4py": {},
    }
    FILE_EXT = "xml"

    def preprocess_code(self):
        self._clean_code_lines("<")
        self._code = self._code.strip()
        if not self._code.startswith("<?xml"):
            self._code = f'<?xml version="1.0" encoding="UTF-8"?>\n{self._code}'

    def _render_graphviz(self):
        def local_name(tag: str) -> str:
            return tag.rsplit("}", 1)[-1] if "}" in tag else tag

        node_types = {
            "startEvent",
            "intermediateCatchEvent",
            "intermediateThrowEvent",
            "endEvent",
            "boundaryEvent",
            "task",
            "userTask",
            "manualTask",
            "serviceTask",
            "scriptTask",
            "sendTask",
            "receiveTask",
            "businessRuleTask",
            "subProcess",
            "callActivity",
            "dataObject",
            "complexGateway",
            "exclusiveGateway",
            "parallelGateway",
            "inclusiveGateway",
            "eventBasedGateway",
        }

        event_types = {
            "startEvent",
            "intermediateCatchEvent",
            "intermediateThrowEvent",
            "endEvent",
            "boundaryEvent",
        }

        node_shapes = {
            "startEvent": "circle",
            "intermediateCatchEvent": "circle",
            "intermediateThrowEvent": "circle",
            "endEvent": "doublecircle",
            "boundaryEvent": "circle",
            "dataObject": "note",
            "complexGateway": "diamond",
            "exclusiveGateway": "diamond",
            "parallelGateway": "diamond",
            "inclusiveGateway": "diamond",
            "eventBasedGateway": "diamond",
        }

        gateway_markers = {
            "exclusiveGateway": "X",
            "parallelGateway": "+",
            "inclusiveGateway": "O",
            "eventBasedGateway": "EV",
            "complexGateway": "*",
        }

        tree = ET.parse(self._filepath_code)
        root = tree.getroot()
        process = None
        for proc in root.findall(".//{*}process"):
            process = proc
            break
        if process is None:
            raise ValueError("No BPMN process found.")

        nodes: dict[str, dict] = {}
        edges: list[dict] = []

        for elem in process.iter():
            node_type = local_name(elem.tag)
            if node_type not in node_types:
                continue
            node_id = elem.get("id")
            if not node_id:
                continue
            nodes[node_id] = {
                "type": node_type,
                "name": elem.get("name", ""),
            }

        for flow in process.findall(".//{*}sequenceFlow"):
            source = flow.get("sourceRef", "")
            target = flow.get("targetRef", "")
            if not source or not target:
                continue
            edges.append(
                {
                    "source": source,
                    "target": target,
                    "name": flow.get("name", ""),
                }
            )

        def node_label(node_type: str, name: str, node_id: str) -> str:
            base_label = name or node_id
            marker = gateway_markers.get(node_type)
            return f"{marker}\n{base_label}" if marker else base_label

        dot = Digraph(
            "bpmn",
            graph_attr={
                "rankdir": "LR",
                "splines": "polyline",
                "nodesep": "0.5",
                "ranksep": "0.7",
                "ordering": "out",
            },
            node_attr={
                "fontsize": "10",
            },
            edge_attr={
                "fontsize": "9",
                "labelfloat": "true",
                "labeldistance": "1.6",
                "labelangle": "0",
            },
        )

        for node_id, node in nodes.items():
            node_type = node["type"]
            name = node["name"]
            shape = node_shapes.get(node_type, "box")
            if node_type in event_types:
                node_attrs = {
                    "shape": shape,
                    "label": "",
                    "xlabel": name or node_id,
                    "fixedsize": "true",
                    "width": "0.7",
                    "height": "0.7",
                }
                if node_type in {"intermediateCatchEvent", "intermediateThrowEvent", "boundaryEvent"}:
                    node_attrs["style"] = "dashed"
                dot.node(node_id, **node_attrs)
            elif node_type == "dataObject":
                dot.node(node_id, label=name or node_id, shape=shape, fontsize="9")
            else:
                dot.node(node_id, label=node_label(node_type, name, node_id), shape=shape)

        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            if source not in nodes:
                dot.node(source, label=source, shape="box", style="dashed")
            if target not in nodes:
                dot.node(target, label=target, shape="box", style="dashed")
            edge_attrs = {}
            if edge["name"]:
                edge_attrs["label"] = edge["name"]
            if edge["name"] and "reject" in edge["name"].lower():
                edge_attrs["minlen"] = "2"
            dot.edge(source, target, **edge_attrs)

        dot.render(self.filepath_image, format="png", cleanup=True)
        self._png_save(self.filepath_image)

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
            stats["start events"] += len(process.findall("bpmn:startEvent", ns))
            stats["end events"] += len(process.findall("bpmn:endEvent", ns))
            stats["tasks"] += len(process.findall("bpmn:task", ns))
            stats["exclusive gateways"] += len(process.findall("bpmn:exclusiveGateway", ns))
            stats["parallel gateways"] += len(process.findall("bpmn:parallelGateway", ns))

            sequence_flows = process.findall("bpmn:sequenceFlow", ns)
            stats["flow lines"] = len(sequence_flows)
            stats["conditional flow lines"] = sum(1 for flow in sequence_flows if flow.find("bpmn:conditionExpression", ns) is not None)
        return StatisticResponse(node_types=[NodeType(type=name, count=count) for name, count in stats.items()])
